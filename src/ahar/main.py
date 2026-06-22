import click
from ahar.commands.init import init


@click.group()
def cli():
    """ahar — agent harness CLI for agentharnesses.io"""


cli.add_command(init)
