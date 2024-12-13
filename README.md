# LMDB Dataset Management Tool

A Python tool for efficiently managing large datasets using LMDB (Lightning Memory-Mapped Database). This tool provides functionality for writing, reading, and recovering datasets with a focus on image and text data.

## Features

- Write datasets to LMDB format
- Recover original files from LMDB databases
- YAML-based configuration
- Command-line interface

## Installation

```sh
cd llm_lmdb
pip install -e .
```

## Usage

```sh
# help message
lmdb-cli help

# write dataset
lmdb-cli write --config config/lmdb_writer.yaml

# recover dataset
lmdb-cli recover --config config/lmdb_recovery.yaml
```



