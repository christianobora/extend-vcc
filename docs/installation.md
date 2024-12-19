# Installation Guide

## Prerequisites

- Python 3.8+
- pip package manager

## Install from PyPI

```bash
pip install extend-vcc
```

## Install from Source

```bash
# Clone the repository
git clone https://github.com/christianobora/extend-vcc.git

# Change directory
cd extend-vcc

# Install in editable mode
pip install -e .

# Install development dependencies
pip install -e .[dev]
```

## Verify Installation

```python
import extend_vcc
print(extend_vcc.__version__)
```