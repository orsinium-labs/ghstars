from __future__ import annotations

from argparse import ArgumentParser
import asyncio
from functools import cached_property
import json
from pathlib import Path
import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportServerError

from ._base import Command


class Fetch(Command):
    """Collect information about stargazers using GitHub GraphQL API.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--token', required=True,
            help='GitHub API token',
        )
        parser.add_argument(
            '--output', type=Path, default=Path('stars.json'),
            help='path where to save the result',
        )
        parser.add_argument(
            '--orgs', nargs='+', required=True,
            help='organizations to fetch stargazers for',
        )
        parser.add_argument(
            '--max-pages', type=int, default=30,
            help='limit how many pages iterate per project',
        )
        parser.add_argument(
            '--min-followers', type=int, default=100,
            help='skip users that have fewer followers',
        )

    async def run_async(self) -> int:
        result = {}
        for org_name in self.args.orgs:
            result[org_name] = await self._query_org(org_name)
        with self.args.output.open('w') as stream:
            json.dump(result, stream, indent=2)
        return 0

    @cached_property
    def _client(self) -> Client:
        assert len(self.args.token) == 40
        transport = AIOHTTPTransport(
            url="https://api.github.com/graphql",
            headers={'Authorization': f'bearer {self.args.token}'},
        )
        return Client(transport=transport, fetch_schema_from_transport=True)

    @cached_property
    def _document(self):
        path = Path(__file__).parent.parent / 'stargazers.gql'
        return gql(path.read_text())

    async def _query_org(self, org_name: str) -> dict[str, dict]:
        async with self._client as session:
            self.print(f'querying {org_name}')
            resp = await session.execute(
                document=self._document,
                variable_values={'org_name': org_name},
                operation_name='getRepos',
            )
            assert resp['organization']['repositories']['totalCount'] <= 100
            repos = resp['organization']['repositories']['nodes']

            # concurrently query info about all repos
            result = {}
            tasks = []
            for repo in repos:
                tasks.append(self._query_repo(session, org_name, repo['name']))
            self.print(f'awaiting additional info for {org_name} repositories')
            star_infos = await asyncio.gather(*tasks)
            for repo, stars in zip(repos, star_infos):
                result[repo['name']] = stars

            return result

    async def _query_repo(
        self,
        session,
        org_name: str,
        repo_name: str,
    ) -> dict[str, dict[str, object]]:
        result = {}
        cursor = None
        for pageno in range(1, self.args.max_pages + 1):
            if pageno >= 4:
                print(f'querying page {pageno} for {org_name}/{repo_name}')
            page_content, cursor = await self._query_repo_page(
                session=session,
                org_name=org_name,
                repo_name=repo_name,
                cursor=cursor,
            )
            result.update(page_content)
            if cursor is None:
                break
        return result

    @backoff.on_exception(
        backoff.expo,
        exception=(TransportServerError, asyncio.TimeoutError),
        max_tries=5,
    )
    async def _query_repo_page(
        self,
        session,
        org_name: str,
        repo_name: str,
        cursor: str | None,
    ) -> tuple[dict[str, dict[str, object]], str | None]:
        resp = await session.execute(
            document=self._document,
            variable_values={
                'number_of_stargazers': 100,
                'org_name': org_name,
                'repo_name': repo_name,
                'cursor': cursor,
            },
            operation_name='getStargazers',
        )
        stargazers = resp['repository']['stargazers']
        users = {}
        for user in stargazers['nodes']:
            if user['followers']['totalCount'] < self.args.min_followers:
                continue

            # parse top repositories of the user
            repos = []
            for subrepo in user['repositories']['nodes']:
                if subrepo['stargazerCount'] < 100:
                    continue
                if subrepo['owner']['login'] != user['login']:
                    continue
                repos.append(dict(
                    name=subrepo['name'],
                    stars=subrepo['stargazerCount'],
                ))

            # parse pinned repositories of the user
            pins = []
            for subrepo in user['pinnedItems']['nodes']:
                if not subrepo:
                    continue
                if subrepo['stargazerCount'] < 100:
                    continue
                pins.append(dict(
                    name=subrepo['name'],
                    owner=subrepo['owner']['login'],
                    stars=subrepo['stargazerCount'],
                ))

            users[user['login']] = dict(
                followers=user['followers']['totalCount'],
                repos=repos,
                pins=pins,
            )

        new_cursor = None
        if len(users) < stargazers['totalCount']:
            edges = stargazers['edges']
            if edges:
                new_cursor = edges[-1]['cursor']

        return users, new_cursor
