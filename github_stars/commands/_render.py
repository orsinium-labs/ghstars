from __future__ import annotations

from argparse import ArgumentParser
import json

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ._base import Command
from .._models import Stars

ROOT = Path(__file__).parent.parent


class Render(Command):
    """Generate HTML page with the most notable stargazers.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--template', type=Path, default=ROOT / 'index.html.j2',
            help='path to the Jinja2 template to render',
        )
        parser.add_argument(
            '--input', type=Path, default=Path('stars.json'),
            help='path to the data dump produced by fetch',
        )
        parser.add_argument(
            '--output', type=Path, default=Path('public', 'index.html'),
            help='path to the file where HTML output should be written',
        )
        parser.add_argument(
            '--title', default='Most notable stargazers',
            help='HTML page title',
        )

    def run(self) -> int:
        env = Environment(loader=FileSystemLoader(self.args.template.parent))
        template = env.get_template(self.args.template.name)
        with self.args.input.open('r') as stream:
            raw_data = json.load(stream)
        stars = Stars(raw_data)
        content = template.render(
            stars=stars,
            title=self.args.title,
        )
        output_path: Path = self.args.output
        output_path.parent.mkdir(exist_ok=True, parents=True)
        output_path.write_text(content)
        return 0
