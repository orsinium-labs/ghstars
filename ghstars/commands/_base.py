from __future__ import annotations

from argparse import ArgumentParser, Namespace
import asyncio
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, TextIO


@dataclass
class Command:
    name: ClassVar[str]
    args: Namespace
    stdout: TextIO

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        pass

    def run(self) -> int:
        return asyncio.run(self.run_async())

    async def run_async(self) -> int:
        raise NotImplementedError

    def print(self, *args: str, end: str = '\n', sep: str = ' ') -> None:
        print(*args, file=self.stdout, end=end, sep=sep)
