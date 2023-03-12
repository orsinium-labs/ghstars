from __future__ import annotations

from argparse import ArgumentParser
import json

from pathlib import Path

from ._base import Command
from .._models import Stars

ROOT = Path(__file__).parent.parent


class TopAuthors(Command):
    """Show most popular projects authored by your stargazers.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--input', type=Path, default=Path('stars.json'),
            help='path to the data dump produced by fetch',
        )
        parser.add_argument(
            '--min-stars', type=int, default=1000,
            help='filter out repos with fewer than that stars',
        )

    def run(self) -> int:
        with self.args.input.open('r') as stream:
            raw_data = json.load(stream)
        stars = Stars(raw_data)
        repos = [u.top_repo for u in stars.users if u.top_repo is not None]
        repos.sort(key=lambda r: r.stars, reverse=True)
        for repo in repos:
            if repo.stars < self.args.min_stars:
                continue
            full_name = f'{repo.owner}/{repo.name}'
            self.print(f'{full_name:50} {repo.stars:>5}')
        return 0
