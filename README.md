# agentharnesses-cli

Command line tools for [agentharnesses.io](http://agentharnesses.io).

## Installation

### From PyPI (once published)

```bash
pip install agentharnesses-cli
```

### From source

```bash
git clone https://github.com/your-org/cli.git
cd cli
pip install .
```

### Development install

```bash
git clone https://github.com/your-org/cli.git
cd cli
pip install -e .
```

The `-e` flag installs in editable mode so changes to the source are reflected immediately without reinstalling.

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

This creates a `harness.yaml` file in the current directory.
