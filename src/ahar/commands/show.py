import re
from dataclasses import dataclass, field
from pathlib import Path

import click

from harnesses_ref.parser import load_leaf_detectors, leaf_type

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_DESC_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)


def _extract_description(path: Path) -> str:
    try:
        text = path.read_text()
    except (UnicodeDecodeError, IsADirectoryError):
        return ""
    m = _FM_RE.match(text)
    if not m:
        return ""
    desc = _DESC_RE.search(m.group(1))
    if not desc:
        return ""
    return desc.group(1).strip().strip('"').strip("'")


@dataclass
class Node:
    name: str
    is_dir: bool
    kind: str = ""  # "root", "routing", "leaf"
    description: str = ""
    children: list = field(default_factory=list)


def _collect_subdir(subdir: Path, detectors: dict, routing_file_name: str) -> Node:
    node = Node(name=subdir.name, is_dir=True)

    routing_file = subdir / routing_file_name
    if routing_file.exists():
        node.children.append(Node(
            name=routing_file_name,
            is_dir=False,
            kind="routing",
            description=_extract_description(routing_file),
        ))

    for item in sorted(subdir.iterdir()):
        if item.name.startswith(".") or item.name == routing_file_name:
            continue
        if not item.is_dir():
            continue
        ltype = leaf_type(item, detectors)
        if ltype is None and (item / "SKILL.md").exists():
            ltype = "skill"
        if ltype == "skill":
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                leaf_dir = Node(name=item.name, is_dir=True)
                leaf_dir.children.append(Node(
                    name="SKILL.md",
                    is_dir=False,
                    kind="leaf",
                    description=_extract_description(skill_md),
                ))
                node.children.append(leaf_dir)
        elif ltype is not None:
            node.children.append(Node(name=item.name, is_dir=True))
        else:
            node.children.append(_collect_subdir(item, detectors, routing_file_name))

    return node


def _render_children(nodes: list, prefix: str, show_desc: bool):
    for i, node in enumerate(nodes):
        is_last = i == len(nodes) - 1
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")
        if node.is_dir:
            click.echo(f"{prefix}{connector}{node.name}/")
            _render_children(node.children, child_prefix, show_desc)
        else:
            label = f"{node.name} [{node.kind}]"
            if show_desc and node.description:
                label += f" — {node.description}"
            click.echo(f"{prefix}{connector}{label}")


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("-v", "--verbosity", default=0, type=click.IntRange(0, 1), help="0=tree with labels (default), 1=tree with descriptions")
def show(path: Path, verbosity: int):
    """Print harness structure as an ASCII tree."""
    harness_md = path / "HARNESS.md"
    if not harness_md.exists():
        click.echo("No HARNESS.md found — not a harness directory.", err=True)
        raise SystemExit(1)

    root_nodes = [Node(
        name="HARNESS.md",
        is_dir=False,
        kind="root",
        description=_extract_description(harness_md),
    )]

    detectors = load_leaf_detectors(path)
    for item in sorted(path.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            routing_file_name = item.name.upper() + ".md"
            root_nodes.append(_collect_subdir(item, detectors, routing_file_name))

    click.echo(f"{path.name}/")
    _render_children(root_nodes, prefix="", show_desc=(verbosity == 1))
