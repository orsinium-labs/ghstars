from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Iterator


@dataclass(frozen=True)
class Repo:
    owner: str
    name: str
    stars: int

    @property
    def url(self) -> str:
        return f'https://github.com/{self.owner}/{self.name}'


@dataclass(frozen=True)
class User:
    name: str
    followers: int
    repos: list[Repo]   # top repos owned by the user
    pins: list[Repo]    # repos pinned by the user
    stars: list[Repo]   # repos that the user starred

    @property
    def weight(self) -> int:
        """Heuristic "notability" of a user.

        Used to sort users when rendering the web page.
        """
        if self.top_repo:
            return max(self.top_repo.stars // 2, self.followers)
        return self.followers

    @cached_property
    def top_repo(self) -> Repo | None:
        if not self.repos:
            return None
        repo = self.repos[0]
        if repo.stars < 2000:
            return None
        return repo

    @cached_property
    def top_pin(self) -> Repo | None:
        if not self.pins:
            return None
        repo = max(self.pins, key=lambda r: r.stars)
        if repo.stars < 2000:
            return None
        if repo.owner == self.name:
            return None
        return repo

    @property
    def url(self) -> str:
        return f'https://github.com/{self.name}'


@dataclass(frozen=True)
class Star:
    repo_name: str
    org_name: str
    user: User


@dataclass(frozen=True)
class Stars:
    items: dict[str, dict[str, dict[str, dict[str, Any]]]]

    def get_top_users(self, min_followers: int) -> Iterator[User]:
        for user in self.users:
            if user.followers < min_followers:
                continue
            is_notable = user.top_repo or user.top_pin or user.followers > 2000
            if is_notable:
                yield user

    @cached_property
    def users(self) -> list[User]:
        grouped: dict[str, User] = {}
        for star in self.stars:
            user = grouped.setdefault(star.user.name, star.user)
            user.stars.append(Repo(
                owner=star.org_name,
                name=star.repo_name,
                stars=0,
            ))
        return sorted(
            grouped.values(),
            key=lambda u: u.weight,
            reverse=True,
        )

    @property
    def stars(self) -> Iterator[Star]:
        for org_name, repos in self.items.items():
            for repo_name, users in repos.items():
                for user_name, user_info in users.items():
                    user = User(
                        name=user_name,
                        followers=user_info['followers'],
                        repos=[
                            Repo(**r, owner=user_name)
                            for r in user_info['repos']
                        ],
                        pins=[
                            Repo(**r)
                            for r in user_info['pins']
                        ],
                        stars=[],
                    )
                    yield Star(
                        repo_name=repo_name,
                        org_name=org_name,
                        user=user,
                    )
