# CSV Data Generator

## Purpose

Generate CSV test data from plain text source files and simple derived rules.

## Features

* Random value selection from `.txt` files
* Derived email generation from first and last name
* Fixed-value columns
* JSON-based configuration
* CSV export

## Project Structure

```text
csv_data_generator/
  data/
  output/
  src/
  tests/
  config.json
```

## Prepare Environment

```shell
cd ./csv_data_generator
python --version
pip install pytest
pip install -e .
```

## Test

```shell
cd ./csv_data_generator
pytest
```

## Run

```shell
cd ./csv_data_generator
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\csv_data_generator
python ./src/main.py --config ./config.json
```

## Configuration

Each column supports one of these types:

* `random_from_file`
* `derived`
* `fixed`

Example:

```json
{
  "row_count": 10,
  "output_file": "output/generated_data.csv",
  "seed": 42,
  "columns": [
    {
      "name": "first_name",
      "type": "random_from_file",
      "file": "data/first_names.txt"
    },
    {
      "name": "last_name",
      "type": "random_from_file",
      "file": "data/last_names.txt"
    },
    {
      "name": "email",
      "type": "derived",
      "method": "email_from_name",
      "domain": "example.com"
    }
  ]
}
```
