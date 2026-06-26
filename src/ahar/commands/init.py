import os
import shutil
import subprocess
import sys
import tempfile
import click

_METASKILL_REPO = "https://github.com/agentharnesses/metaskill"
_METASKILL_DEST = ".claude/skills/agent-harnesses"

_MAINTAIN_SKILL_DEST = "skills/maintenance/modify-harness/SKILL.md"
_MAINTAIN_SKILLS_INDEX_DEST = "skills/maintenance/SKILLS.md"

_MAINTAIN_SKILL = """\
---
name: modify-harness
description: Update harness structure files — HARNESS.md, SKILLS.md indexes, REFERENCES.md — to keep routing and descriptions accurate as the harness evolves.
---

## Role

Keep the harness self-consistent when skills or references are added, renamed, or removed.

## What to do

1. Use reverse progressive disclosure (via the `agent-harnesses` skill) to find which index files reference the target path
2. Read the current state of each affected file
3. Apply the change: add, update, or remove the relevant entry
4. Ensure descriptions remain accurate and routing summaries reflect actual contents

## Conventions

- Keep `HARNESS.md` `## Skills` and `## References` sections in sync with `skills/SKILLS.md` and `references/REFERENCES.md`
- Update the `description` frontmatter in `HARNESS.md` when the harness scope changes
- Skill descriptions should be actionable: "Use when..." not "This skill..."
- Reference documents should be stable facts; skill buckets contain executable guidance
- Prefer updating existing skill buckets over creating new ones when scope overlaps
"""

_MAINTAIN_SKILLS_INDEX = """\
---
description: Harness upkeep skills — for modifying the harness structure, adding skills and references.
---

- [modify-harness](modify-harness/SKILL.md) — Use when maintaining or extending this harness
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
description: TODO describe what this harness does and the role it gives Claude.
---

## Upon loading the Harness

TODO: write the entry message Claude should internalize when this harness loads.

## How to Find Information for Claude

Use the `agent-harnesses` skill to explore the harness just in time, based on prompts from the user. Select only what is relevant and repeat until the session is complete, then read the returned resources.

When **maintaining the harness** (adding, moving, or renaming files), consult the `agent-harnesses` skill for reverse progressive disclosure to keep routing files in sync.

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
        f"{root}/.gitignore",
        """\
# Claude settings contain absolute paths — keep local
.claude/settings.json
.claude/settings.local.json

# Metaskill session state
.claude/skills/agent-harnesses/sessions/

# Mac
.DS_Store
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
        f"{root}/.leaf-detectors",
        """\
skill=SKILL.md
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
    click.echo("  .gitignore")
    click.echo("  .leaf-detectors")
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
        click.echo(f"Metaskill already present at {_METASKILL_DEST} — skipping.")
        return

    click.echo("Cloning metaskill...")
    with tempfile.TemporaryDirectory() as tmp:
        clone_dir = os.path.join(tmp, "metaskill")
        result = subprocess.run(
            ["git", "clone", _METASKILL_REPO, clone_dir],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            click.echo(f"Clone failed:\n{result.stderr.strip()}", err=True)
            sys.exit(1)

        src = os.path.join(clone_dir, "agent-harnesses")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copytree(src, dest)

    click.echo(f"  {_METASKILL_DEST}")


def _install_maintain_skill(root):
    skill_dest = os.path.join(root, _MAINTAIN_SKILL_DEST)
    index_dest = os.path.join(root, _MAINTAIN_SKILLS_INDEX_DEST)

    if os.path.exists(skill_dest):
        click.echo(f"maintain-harness skill already present — skipping.")
        return

    _write(index_dest, _MAINTAIN_SKILLS_INDEX)
    click.echo(f"  {_MAINTAIN_SKILLS_INDEX_DEST}")

    _write(skill_dest, _MAINTAIN_SKILL)
    click.echo(f"  {_MAINTAIN_SKILL_DEST}")
