import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from ahar.commands.init import scaffold
from ahar.main import cli


# --- scaffold unit tests ---

def test_scaffold_creates_required_files(tmp_path):
    scaffold(str(tmp_path), "my-harness")
    assert (tmp_path / "HARNESS.md").exists()
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / ".gitignore").exists()
    assert (tmp_path / ".claude" / "settings.json").exists()
    assert (tmp_path / "skills" / "SKILLS.md").exists()
    assert (tmp_path / "references" / "REFERENCES.md").exists()


def test_scaffold_harness_md_contains_name(tmp_path):
    scaffold(str(tmp_path), "my-harness")
    content = (tmp_path / "HARNESS.md").read_text()
    assert "name: my-harness" in content


def test_scaffold_settings_registers_marketplace(tmp_path):
    scaffold(str(tmp_path), "my-harness")
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    assert "my-harness" in settings["extraKnownMarketplaces"]
    assert settings["extraKnownMarketplaces"]["my-harness"]["source"]["source"] == "directory"
    assert settings["extraKnownMarketplaces"]["my-harness"]["source"]["path"] == str(tmp_path)


def test_scaffold_settings_enables_plugin(tmp_path):
    scaffold(str(tmp_path), "my-harness")
    settings = json.loads((tmp_path / ".claude" / "settings.json").read_text())
    assert "my-harness@my-harness" in settings["enabledPlugins"]
    assert settings["enabledPlugins"]["my-harness@my-harness"] is True


def test_scaffold_gitignore_excludes_settings(tmp_path):
    scaffold(str(tmp_path), "my-harness")
    content = (tmp_path / ".gitignore").read_text()
    assert ".claude/settings.json" in content


# --- init CLI tests ---

def test_init_empty_preset_creates_scaffold(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-harness"], input="empty\n")
        assert result.exit_code == 0
        assert Path("HARNESS.md").exists()
        assert Path("skills/SKILLS.md").exists()
        assert Path("references/REFERENCES.md").exists()


def test_init_uses_directory_name_as_default(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init"], input="empty\n")
        assert result.exit_code == 0
        content = Path("HARNESS.md").read_text()
        assert f"name: {Path.cwd().name}" in content


def test_init_fails_if_already_initialized(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("HARNESS.md").write_text("---\nname: existing\ndescription: x\n---\n")
        result = runner.invoke(cli, ["init"], input="empty\n")
        assert result.exit_code == 1


def test_init_empty_preset_skips_metaskill(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-harness"], input="empty\n")
        assert result.exit_code == 0
        assert not Path(".claude/skills/agent-harnesses").exists()


# --- validate CLI tests ---

def _make_valid_harness(path: Path) -> Path:
    (path / "HARNESS.md").write_text(
        "---\nname: Test Harness\ndescription: A test harness.\n---\nBody.\n"
    )
    return path


def test_validate_valid_harness(tmp_path):
    _make_valid_harness(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(tmp_path)])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_validate_invalid_harness(tmp_path):
    (tmp_path / "HARNESS.md").write_text("no frontmatter")
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", str(tmp_path)])
    assert result.exit_code == 1


# --- read CLI tests ---

def test_read_name(tmp_path):
    _make_valid_harness(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["read", str(tmp_path), "name"])
    assert result.exit_code == 0
    assert result.output.strip() == "Test Harness"


def test_read_description(tmp_path):
    _make_valid_harness(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["read", str(tmp_path), "description"])
    assert result.exit_code == 0
    assert result.output.strip() == "A test harness."


# --- prompt CLI tests ---

def test_prompt_renders_xml(tmp_path):
    _make_valid_harness(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["prompt", str(tmp_path)])
    assert result.exit_code == 0
    assert "<harness" in result.output
    assert "Test Harness" in result.output
