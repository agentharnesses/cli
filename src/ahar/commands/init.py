import os
import subprocess
import sys
import click

_METASKILL_REPO = "https://github.com/agentharnesses/metaskill"  # TODO: replace with final URL
_METASKILL_DEST = ".claude/plugins/metaskill"
_MAINTAIN_SKILL_DEST = ".claude/skills/maintain-harness.md"

_MAINTAIN_SKILL = """\
---
name: maintain-harness
description: How to maintain and update this harness — updating HARNESS.md, adding skills and references, managing the skill index.
---

## Maintaining the Harness

When asked to maintain, update, or extend this harness, follow these conventions:

### HARNESS.md
- Keep the `## Skills` section in sync with entries in `skills/SKILLS.md`
- Keep the `## References` section in sync with entries in `references/REFERENCES.md`
- Update the `description` frontmatter field when the harness scope changes

### Adding a skill bucket
1. Create `skills/<bucket-name>/<bucket-name>.md` with a frontmatter `name` and `description`
2. Add an entry to `skills/SKILLS.md` summarizing when to use the bucket
3. Add a bullet to the `## Skills` section in `HARNESS.md`

### Adding a reference document
1. Add the document to `references/`
2. Add an entry to `references/REFERENCES.md` describing the document's purpose
3. Add a bullet to the `## References` section in `HARNESS.md`

### General conventions
- Keep skill descriptions actionable: "Use when..." not "This skill..."
- Reference documents should be stable facts; skill buckets contain executable guidance
- Prefer updating existing skill buckets over creating new ones when scope overlaps
"""


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

TODO: add reference documents here as they are added.
""",
    )


_PRESETS = {
    "claude": "Full Claude Code setup: metaskill plugin + maintain-harness skill",
    "empty":  "Bare minimum: no additional plugins or skills",
}


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

    click.echo("\nClaude Code preset:")
    for key, desc in _PRESETS.items():
        click.echo(f"  {key:<8} {desc}")

    preset = click.prompt(
        "Preset",
        type=click.Choice(list(_PRESETS.keys()), case_sensitive=False),
        default="claude",
        show_choices=False,
    )
    _configure_claude(cwd, preset)


def _configure_claude(root, preset):
    if preset == "empty":
        click.echo("Skipping Claude Code plugin configuration (empty preset).")
        return

    # claude preset: metaskill + maintain-harness skill
    _install_metaskill(root)
    _install_maintain_skill(root)


def _install_metaskill(root):
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


def _install_maintain_skill(root):
    dest = os.path.join(root, _MAINTAIN_SKILL_DEST)
    if os.path.exists(dest):
        click.echo(f"maintain-harness skill already present at {_MAINTAIN_SKILL_DEST} — skipping.")
        return
    _write(dest, _MAINTAIN_SKILL)
    click.echo(f"  {_MAINTAIN_SKILL_DEST}")
