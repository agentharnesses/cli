# agentharnesses-cli

CLI for [agentharnesses.io](https://agentharnesses.io) — scaffold and manage Agent Harnesses.

## Installation

```bash
pip install agentharnesses-cli
```

## Usage

```bash
ahar --help
```

### `ahar init`

Initialize a new harness in the current directory:

```bash
ahar init
```

Optionally specify a name (defaults to the directory name):

```bash
ahar init my-harness
```

Scaffolds the following structure:

```
my-harness/
├── HARNESS.md                       # entry point and agent identity
├── README.md                        # human-facing description
├── .gitignore
├── .claude/settings.json            # registers the harness as a Claude Code plugin
├── skills/
│   └── SKILLS.md                    # skill index
└── references/
    └── REFERENCES.md                # reference index
```

When using the `claude` preset (default), also installs:

```
├── .claude/skills/agent-harnesses/  # metaskill for progressive harness exploration
└── skills/
    └── maintenance/
        ├── SKILLS.md
        └── modify-harness/
            └── SKILL.md
```

The metaskill is cloned fresh from [agentharnesses/metaskill](https://github.com/agentharnesses/metaskill) at init time, so you always get the latest version.

## Publishing

Releases are published to PyPI automatically when a version tag is pushed:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The GitHub Actions workflow builds the package and publishes it via trusted publishing (no API token required). The version is derived from the tag via `hatch-vcs`.

## License

Apache 2.0
