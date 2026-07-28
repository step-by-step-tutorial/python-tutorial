# CSV Data Generator

## Purpose

Generate CSV test data from plain text source files, numeric/date generators, and derived lookup rules.

## Features

* Random value selection from `.txt` files
* Country-aware source files via a mapping CSV, optionally joining several mapped files into one column
* Derived field generation from row values or lookup files
* Fixed-value columns
* Sequential identifiers
* Random integer generation
* Random date generation
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
* `random_from_mapped_file`
* `derived`
* `fixed`
* `sequence`
* `random_int`
* `random_date`

Column order in `columns` is the column order of the generated CSV. Dependencies between columns
are resolved automatically, so a column may reference a `source_field` that is listed after it.

`random_from_mapped_file` takes either a single `file_column` or a list of `file_columns`. With a
list, one random value is picked per mapped file and the values are joined with `separator`
(a single space by default) — for example a first-name file plus a last-name file to build a
full name from the same country.

Example:

```json
{
  "row_count": 10,
  "output_file": "output/generated_orders.csv",
  "seed": 42,
  "columns": [
    {
      "name": "order_id",
      "type": "sequence",
      "start": 1,
      "step": 1
    },
    {
      "name": "customer_name",
      "type": "random_from_mapped_file",
      "source_field": "country",
      "mapping_file": "data/country_source_map.csv",
      "key_column": "country",
      "file_columns": ["first_name_file", "last_name_file"],
      "separator": " "
    },
    {
      "name": "product_name",
      "type": "random_from_file",
      "file": "data/product_names.txt"
    },
    {
      "name": "category",
      "type": "derived",
      "method": "lookup_from_csv",
      "source_field": "product_name",
      "mapping_file": "data/product_catalog.csv",
      "key_column": "product",
      "value_column": "category"
    },
    {
      "name": "quantity",
      "type": "random_int",
      "min": 1,
      "max": 5
    },
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
    {
      "name": "country",
      "type": "random_from_file",
      "file": "data/countries.txt"
    }
  ]
}
```

Output:

```text
order_id,customer_name,product_name,category,quantity,unit_price,order_date,country
1,Lea Bauer,Mouse,Electronics,2,25,2026-01-12,Germany
2,Michael Wilson,Microphone,Electronics,5,130,2026-01-07,USA
```

## Data Files

| File | Contents |
| --- | --- |
| `data/countries.txt` | Countries wired up in `data/country_source_map.csv` (Germany, USA, UK, Canada) |
| `data/countries_iso.txt` | All 249 ISO 3166-1 country names, for configs that do not need per-country source files |
| `data/country_source_map.csv` | Per-country first name, last name, phone, and address files |
| `data/product_names.txt` | Product pool the `product_name` column draws from |
| `data/product_catalog.csv` | 10,000 products with `category` and `unit_price`, keyed by `product` |