# Test Data Generator

Generate realistic CSV test data from plain text source files, numeric and date generators, and
derived lookup rules — all driven by a JSON config file, with no code changes needed for a new
dataset.

Every dataset is described by one config file. The generator reads the config, pulls values from
the files under `data/`, and writes a CSV to `output/`. Because related values are pulled through
mapping files, a row stays internally consistent: a German customer gets a German first name, a
German phone number, a German address, and `EUR`.

## Table of Contents

* [Features](#features)
* [Prerequisites](#prerequisites)
* [Project Structure](#project-structure)
* [Prepare Environment](#prepare-environment)
* [Run the Application](#run-the-application)
* [Run the Tests](#run-the-tests)
* [Configuration Guide](#configuration-guide)
  * [Top-Level Keys](#top-level-keys)
  * [Column Types](#column-types)
  * [Column Order and Dependencies](#column-order-and-dependencies)
  * [Weighting Values](#weighting-values)
  * [Path Resolution](#path-resolution)
  * [Reproducible Output](#reproducible-output)
  * [Example](#example)
* [Datasets](#datasets)
* [Data Files](#data-files)
* [Add a New Dataset](#add-a-new-dataset)
* [Design Notes and Limits](#design-notes-and-limits)
* [Troubleshooting](#troubleshooting)

## Features

* Random value selection from `.txt` files
* Country-aware source files via a mapping CSV, optionally joining several mapped files into one column
* Derived fields from other columns in the same row, or from a lookup CSV
* Fixed-value columns
* Sequential identifiers
* Random integer generation
* Random date generation
* Automatic dependency resolution between columns, independent of column order
* Reproducible output through a project-wide random seed
* JSON-based configuration, one file per dataset
* Configurable destinations per dataset: CSV, JSON, database, or Kafka
* CSV export with quoting handled by the standard library

## Prerequisites
* Python

No third-party runtime dependencies — the generator uses only the Python standard library.

## Project Structure

```text
test_data/
  config/
    sale.json                       dataset config: minimal order sample
    online_shopping.json            dataset config: online shopping orders
    hr.json                         dataset config: HR employee records
  pyproject.toml
  data/                             source values, organised by kind of data
  output/                           generated CSV files (git-ignored)
  src/
    main.py                         script entry point for `python ./src/main.py`
    api.py                          FastAPI service entry point
    cli.py                          installed CLI command
    columns.py                      column generators and derived-value helpers
    database_repository.py          writes generated rows into the test-data database
    application_config.py                       config models and JSON loading
    datasets.py                     dataset registry and output metadata
    exceptions.py                   package-specific error types
    generator.py                    row generation orchestration
    json_writer.py                  JSON output writer
    schemas.py                      API request and response schemas
    sources.py                      source file and mapping loaders
    writer.py                       CSV writing
  tests/
    test_generator.py
    test_config.py
    test_columns.py
```

`data/` is organised by kind of data, never by dataset: `first_names/`, `product_names.txt`,
`job_titles/`, and so on. A folder holds one file per key of the mapping that selects it —
`first_names/germany.txt` is keyed by country, `job_titles/engineering.txt` by department. Any
config may draw from any of these files, so a new dataset usually needs no new folders.

One config file per dataset, stored under `config/`, with any `.json` name:

## Prepare Environment

```shell
cd ./test_data
python --version
python -m venv .venv
```

Activate the virtual environment — PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Bash (Git Bash, Linux, macOS):

```shell
source .venv/Scripts/activate   # Windows
source .venv/bin/activate       # Linux / macOS
```

Then install what you need:

```shell
pip install pytest
pip install -e .
```

Both installs are optional: `pytest` is needed only to run the tests, and `pip install -e .` only
makes the modules under `src/` importable from outside `pytest`. Running the generator itself needs
nothing installed.

## Run the Tests

```shell
cd ./test_data
pytest
```

`pyproject.toml` points pytest at `tests/` and puts `src` on the path, so no extra flags are needed.
The suite covers email normalisation, CSV writing, every column type, joined mapped files,
dependency resolution across column order, and rejection of circular dependencies.

## Run the Application

`--config` is required — it selects the dataset. Run from the `test_data` folder:

```shell
cd ./test_data
docker compose --file docker-compose.yml --project-name test --env-file ./.env.test down -v
docker compose --file docker-compose.yml --project-name test --env-file ./.env.test up --build -d
```

```shell
cd ./test_data
python ./src/main.py --config ./config/sale.json
python ./src/main.py --config ./config/online_shopping.json
python ./src/main.py --config ./config/hr.json
python ./src/main.py --help
```

```shell
cd ./test_data
Set-Location C:\Users\saman\IdeaProjects\python-tutorial\test_data
python ./src/dataset_api.py 
```

URL: [localhost:8080](http://localhost:8080)
API Documentation: [localhost:8080/docs](http://localhost:8080/docs)
API Documentation: [localhost:8080/redoc](http://localhost:8080/redoc)

```shell
cd ./test_data
docker compose --file docker-compose.yml --project-name test --env-file ./.env.test down -v
```

The output file is overwritten on every run, and `output/` is created if missing. Generated CSVs are
git-ignored, so the repository keeps the inputs, not the results.

## Configuration Guide

A config file is a JSON object with three required keys plus the column list.

### Top-Level Keys

| Key | Required | Description |
| --- | --- | --- |
| `row_count` | yes | Number of data rows to generate |
| `output_file` | yes | Destination CSV, relative to the project root |
| `column_generator.py` | yes | Ordered list of column definitions |
| `destinations` | no | Output targets to write: `csv`, `json`, `database`, or `kafka` |

### Column Types

Every column needs a `name` and a `type`. The remaining keys depend on the type.

| Type | Keys | Description |
| --- | --- | --- |
| `random_from_file` | `file` | Random line from a `.txt` file |
| `random_from_mapped_file` | `source_field`, `mapping_file`, `key`, `file_column` or `file_columns`, `separator` | Random line from the file that the mapping CSV lists for another column's value |
| `derived` | `method` plus the method's own keys | Value computed from other columns in the same row |
| `fixed` | `value` | The same literal in every row |
| `sequence` | `start`, `step` | Incrementing integer; both default to `1` |
| `random_int` | `min`, `max` | Random integer, both bounds inclusive |
| `random_date_between` | `date_start`, `date_end` | Random ISO date, both bounds inclusive |

`derived` supports two methods:

| Method | Keys | Description |
| --- | --- | --- |
| `email_from_source_fields` | `source_fields`, `domain` (defaults to `example.com`) | Builds an email local part from configured fields, stripping accents and punctuation (`Jalalé` becomes `jalale`) |
| `product_of_source_fields` | `source_fields`, optional `value` | Multiplies the numeric fields listed in `source_fields` and, if present, an optional constant `value` |
| `formula` | `source_fields`, `formula` | Evaluates arithmetic using the numeric source values |
| `lookup_from_csv` | `source_field`, `mapping_file`, `key`, `value` | Looks another column's value up in a CSV and returns one of its fields |

`email_from_source_fields` joins configured source fields with `.`, so the source columns can have
any names and the derived column can be named anything, such as `work_email`.

`product_of_source_fields` takes one or more `source_fields`. The output column can be named
anything, such as `subtotal`, `line_total`, or `gross_amount`. If you also provide `value`, it is
multiplied in as a constant factor.

`formula` receives source values as an ordered `values` list. For example,
`values[0] - values[0] * values[1] / 100 + values[2] + values[3]` uses four configured
source fields without requiring particular field names.

`random_from_mapped_file` takes either a single `file_column` or a list of `file_columns`. With a
list, one random value is picked per mapped file and the values are joined with `separator`
(a single space by default) — for example a first-name file plus a last-name file to build a full
name from the same country:

```json
{
  "name": "customer_name",
  "type": "random_from_mapped_file",
  "source_field": "country",
  "mapping_file": "data/country_source_map.csv",
  "key_column": "country",
  "file_columns": ["first_name_file", "last_name_file"],
  "separator": " "
}
```

Mapping files come in two shapes, and one CSV can serve both. A **file map** holds paths, for
`random_from_mapped_file`:

```text
country,first_name_file,last_name_file,phone_file,address_file
Germany,data/first_names/germany.txt,data/last_names/germany.txt,data/phones/germany.txt,data/addresses/germany.txt
```

A **value map** holds literals, for `lookup_from_csv`:

```text
country,currency_code,timezone
Germany,EUR,Europe/Berlin
```

### Column Order and Dependencies

The order of `attribute.py` is the column order of the generated CSV. Dependencies are resolved
automatically, so a column may reference a `source_field` that is declared *after* it — which is how
`country` can be the last column while the name, phone, and address columns all follow from it.
Circular references are rejected with a clear error instead of hanging.

### Weighting Values

`random_from_file` picks a line uniformly at random, so repeating a line makes it more likely.
`data/order_statuses.txt` lists `Delivered` 3 times out of 14 lines, and `data/coupon_codes.txt`
lists `NONE` 6 times out of 16 so that roughly 38% of orders carry no coupon.

### Path Resolution

Every path inside a config — `output_file`, `file`, `mapping_file`, and the paths stored *inside* a
file map — resolves relative to the folder holding the config file, not to the current working
directory. Running `python ./src/main.py --config ./config/hr.json` from any directory therefore
resolves `data/departments.txt` inside the project root.

### Reproducible Output

`env_config.RANDOM_SEED` makes every run reproducible: the same config plus the same data files
produce a byte-identical CSV. Editing a data file changes the output because the random draws consume
that file's lines.

### Example

```json
{
  "row_count": 10,
  "output_file": "output/sales.csv",
  "columns": [
    { "name": "order_id", "type": "sequence", "start": 1, "step": 1 },
    {
      "name": "customer_name",
      "type": "random_from_mapped_file",
      "source_field": "country",
      "mapping_file": "data/country_source_map.csv",
      "key_column": "country",
      "file_columns": ["first_name_file", "last_name_file"],
      "separator": " "
    },
    { "name": "product_name", "type": "random_from_file", "file": "data/product_names.txt" },
    {
      "name": "category",
      "type": "derived",
      "method": "lookup_from_csv",
      "source_field": "product_name",
      "mapping_file": "data/product_catalog.csv",
      "key_column": "product",
      "value_column": "category"
    },
    { "name": "quantity", "type": "random_int", "min": 1, "max": 5 },
    {
      "name": "unit_price",
      "type": "derived",
      "method": "lookup_from_csv",
      "source_field": "product_name",
      "mapping_file": "data/product_catalog.csv",
      "key_column": "product",
      "value_column": "unit_price"
    },
    {
      "name": "order_date",
      "type": "random_date",
      "date_start": "2026-01-05",
      "date_end": "2026-01-31"
    },
    { "name": "country", "type": "random_from_file", "file": "data/countries.txt" }
  ]
}
```

## Data Files

Counts are values available, not rows generated.

| File | Values | Contents |
| --- | --- | --- |
| `data/countries.txt` | 4 | Countries wired up in the mapping files: Germany, USA, UK, Canada |
| `data/countries_iso.txt` | 249 | All ISO 3166-1 country names, for configs that need no per-country source files |
| `data/first_names/*.txt` | 4 × 1000 | First names per country |
| `data/last_names/*.txt` | 4 × 1000 | Last names per country |
| `data/phones/*.txt` | 4 × 1000 | Phone numbers per country |
| `data/addresses/*.txt` | 4 × 1000 | Street addresses per country |
| `data/country_source_map.csv` | 4 rows | Country to its first name, last name, phone, and address files |
| `data/country_profile_map.csv` | 4 rows | Country to `currency_code` and `timezone` |
| `data/product_names.txt` | 10000 | Product pool the `product_name` column draws from |
| `data/product_catalog.csv` | 10000 rows | Products with `category` and `unit_price`, keyed by `product` |
| `data/sales_channels.txt` | 7 | Web Store, iOS App, Marketplace, ... |
| `data/payment_methods.txt` | 10 | Credit Card, PayPal, Klarna, ... |
| `data/shipping_methods.txt` | 8 | Standard, Express, Pickup Point, ... |
| `data/order_statuses.txt` | 14 | Order lifecycle states, `Delivered` weighted |
| `data/coupon_codes.txt` | 16 | Coupon codes plus repeated `NONE` entries |
| `data/country_warehouse_map.csv` | 4 rows | Country to warehouse file |
| `data/warehouses/*.txt` | 17 | Warehouses per country |
| `data/departments.txt` | 10 | Departments |
| `data/department_job_map.csv` | 10 rows | Department to job title file |
| `data/job_titles/*.txt` | 74 | Job titles per department |
| `data/seniority_levels.txt` | 8 | Intern through Director |
| `data/salary_bands.csv` | 8 rows | Seniority level to `salary_grade` and `base_salary_usd` |
| `data/employment_types.txt` | 6 | Full-time, Contract, Internship, ... |
| `data/work_modes.txt` | 3 | On-site, Hybrid, Remote |
| `data/employment_statuses.txt` | 7 | Active, Probation, Notice Period, ... |
| `data/country_office_map.csv` | 4 rows | Country to office file |
| `data/offices/*.txt` | 17 | Offices per country |

## Add a New Dataset

1. Copy `config/sale.json` to `config/<dataset>.json` and set `row_count` and `output_file`.
2. Reuse the existing files under `data/` wherever possible — most datasets need no new data.
3. For genuinely new values, add a file named after the *kind* of data, not the dataset:
   `data/<kind>.txt` for a flat list, or `data/<kind>/<key>.txt` plus a mapping CSV when the values
   depend on another column.
4. Define the columns in the order you want them in the CSV; ignore dependency order.
5. Generate it: `python ./src/main.py --config ./config/<dataset>.json`.
6. Add the config to the dataset table above and any new files to the data file table.

## Design Notes and Limits

* Every value is written as text, but derived methods can still express simple arithmetic such as
  a `subtotal` equal to `quantity × unit_price`.
* `random_int` and `random_date_between` produce integers and ISO dates only; there is no decimal or
  timestamp type.
* Dates are drawn independently, so a config cannot express "delivery date is 3 days after order
  date". `config/online_shopping.json` uses a `delivery_days` integer for that reason.
* Values are drawn per row with replacement, so a column is not unique unless it is a `sequence`.
* `row_count` rows are held in memory before being written, which is fine for the current datasets
  but not for tens of millions of rows.
* Source files are read once and cached per run, so editing a data file mid-run has no effect.
* Lines in a `.txt` file are stripped, and blank lines are ignored.

## Troubleshooting

| Message | Cause |
| --- | --- |
| `the following arguments are required: --config` | `--config` is mandatory; pass a config file |
| `FileNotFoundError` on a data file | A `file` or `mapping_file` path is wrong, or the command was run from a folder that does not contain the config |
| `Source file is empty: <path>` | A `.txt` source has no non-blank lines |
| `Value 'X' not found in mapping for column 'Y'` | The source column produced a value with no row in the mapping CSV — for example pointing `country` at `countries_iso.txt` while the mapping only covers 4 countries |
| `Column 'X' depends on unknown column 'Y'` | `source_field` names a column that no config entry defines |
| `Circular column dependency detected: a -> b -> a` | Two columns reference each other through `source_field` |
| `Mapping file '<path>' must contain columns 'k' and 'v'` | `key`, `value`, or `file_column` does not match the CSV header |
| `Use either file_column or file_columns, not both` | A `random_from_mapped_file` column sets both keys |
| `Columns of type random_int require min and max` | `min` or `max` is missing |
| `date_start must be earlier than or equal to date_end` | The date range is inverted |
| `Unsupported column type: X` / `Unsupported derived method: X` | A typo in `type` or `method` |
| `Column 'X' depends on unknown column 'Y'` | An `email_from_source_fields` source field does not exist in the config |
