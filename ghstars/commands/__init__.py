from __future__ import annotations

from types import MappingProxyType

from ._base import Command
from ._fetch import Fetch
from ._render import Render
from ._top_authors import TopAuthors
from ._version import Version


commands: MappingProxyType[str, type[Command]]
commands = MappingProxyType({
    'fetch': Fetch,
    'render': Render,
    'top-authors': TopAuthors,
    'version': Version,
})

__all__ = [
    'commands',
    'Command',
]
