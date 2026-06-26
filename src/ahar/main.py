import click
from ahar.commands.init import init
from ahar.commands.show import show
from harnesses_ref.cli import validate_cmd, read, prompt


@click.group()
def cli():
    """ahar — agent harness CLI for agentharnesses.io"""


cli.add_command(init)
cli.add_command(validate_cmd, name="validate")
cli.add_command(read)
cli.add_command(prompt)
cli.add_command(show)
