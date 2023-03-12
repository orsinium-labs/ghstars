from __future__ import annotations

from argparse import ArgumentParser
import json

from pathlib import Path

from ._base import Command
from .._models import Stars

ROOT = Path(__file__).parent.parent


class TopFollowed(Command):
    """Show stargazers with the most followers.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--input', type=Path, default=Path('stars.json'),
            help='path to the data dump produced by fetch',
        )
        parser.add_argument(
            '--min-followers', type=int, default=1000,
            help='filter out users with fewer than that followers',
        )

    def run(self) -> int:
        with self.args.input.open('r') as stream:
            raw_data = json.load(stream)
        stars = Stars(raw_data)
        users = sorted(stars.users, key=lambda u: u.followers, reverse=True)
        for user in users:
            if user.followers < self.args.min_followers:
                continue
            self.print(f'{user.name:20} {user.followers:>5}')
        return 0
