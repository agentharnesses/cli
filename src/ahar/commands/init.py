import os
import subprocess
import sys
import click

_METASKILL_REPO = "https://github.com/agentharnesses/metaskill"  # TODO: replace with final URL
_METASKILL_DEST = ".claude/plugins/metaskill"


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def scaffold(root, name):
    _write(
        f"{root}/HARNESS.md",
        f"""\
---
name: {name}
description: TODO: describe what this harness does and the role it gives Claude.
---

## Upon loading the Harness

TODO: write the entry message Claude should internalize when this harness loads.

## Skills

TODO: list skill buckets here as they are created.
- See `skills/SKILLS.md` for the full index.

## References

TODO: list reference documents here as they are added.
- See `references/REFERENCES.md` for the full index.
""",
    )

    _write(
        f"{root}/README.md",
        f"""\
# {name}

TODO: brief description of this harness.
""",
    )

    _write(
        f"{root}/.claude/settings.json",
        f"""\
{{
  "extraKnownMarketplaces": {{
    "{name}": {{
      "source": {{
        "source": "directory",
        "path": "{root}"
      }}
    }}
  }},
  "enabledPlugins": {{
    "{name}@{name}": true
  }}
}}
""",
    )

    _write(
        f"{root}/skills/SKILLS.md",
        """\
---
description: TODO: describe the skill buckets in this harness and when to use each.
---

TODO: add skill buckets here as they are created.
""",
    )

    _write(
        f"{root}/references/REFERENCES.md",
        """\
---
description: TODO: describe the reference documents in this harness and how to use them.
---

TODO: add reference documents here as they are created.
""",
    )


@click.command()
@click.argument("name", default=None, required=False)
def init(name):
    """Initialize a new harness in the current directory."""
    cwd = os.getcwd()

    if name is None:
        name = os.path.basename(cwd)

    if os.path.exists(os.path.join(cwd, "HARNESS.md")):
        click.echo("HARNESS.md already exists here — already initialized.", err=True)
        sys.exit(1)

    scaffold(cwd, name)

    click.echo(f"Initialized harness '{name}' in {cwd}")
    click.echo("  HARNESS.md")
    click.echo("  README.md")
    click.echo("  .claude/settings.json")
    click.echo("  skills/SKILLS.md")
    click.echo("  references/REFERENCES.md")

    if click.confirm("\nConfigure Claude Code for this harness?", default=True):
        _configure_claude(cwd)


def _configure_claude(root):
    dest = os.path.join(root, _METASKILL_DEST)
    if os.path.exists(dest):
        click.echo(f"Metaskill already present at {_METASKILL_DEST} — skipping clone.")
        return

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    click.echo(f"Cloning metaskill into {_METASKILL_DEST}...")
    result = subprocess.run(
        ["git", "clone", _METASKILL_REPO, dest],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        click.echo(f"Clone failed:\n{result.stderr.strip()}", err=True)
        sys.exit(1)
    click.echo(f"  {_METASKILL_DEST}")
