from __future__ import annotations

from argparse import ArgumentParser

from ._base import Command


class Version(Command):
    """Print the version of the tool.
    """

    def run(self) -> int:
        from ghstars import __version__
        self.print(__version__)
        return 0
