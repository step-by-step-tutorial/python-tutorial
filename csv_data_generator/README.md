# CSV Data Generator

## Purpose

Generate CSV test data from plain text source files, numeric/date generators, and derived lookup rules.

## Features

* Random value selection from `.txt` files
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
      "name": "country",
      "type": "random_from_file",
      "file": "data/countries.txt"
    },
    {
      "name": "customer_first_name",
      "type": "random_from_mapped_file",
      "source_field": "country",
      "mapping_file": "data/country_source_map.csv",
      "key_column": "country",
      "file_column": "first_name_file"
    },
    {
      "name": "customer_last_name",
      "type": "random_from_mapped_file",
      "source_field": "country",
      "mapping_file": "data/country_source_map.csv",
      "key_column": "country",
      "file_column": "last_name_file"
    },
    {
      "name": "customer_phone",
      "type": "random_from_mapped_file",
      "source_field": "country",
      "mapping_file": "data/country_source_map.csv",
      "key_column": "country",
      "file_column": "phone_file"
    },
    {
      "name": "customer_address",
      "type": "random_from_mapped_file",
      "source_field": "country",
      "mapping_file": "data/country_source_map.csv",
      "key_column": "country",
      "file_column": "address_file"
    },
    {
      "name": "product",
      "type": "random_from_file",
      "file": "data/product_names.txt"
    },
    {
      "name": "category",
      "type": "derived",
      "method": "lookup_from_csv",
      "source_field": "product",
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
      "source_field": "product",
      "mapping_file": "data/product_catalog.csv",
      "key_column": "product",
      "value_column": "unit_price"
    },
    {
      "name": "order_date",
      "type": "random_date",
      "date_start": "2026-01-05",
      "date_end": "2026-01-31"
    }
  ]
}
```

## Country-Based Sources

Country-specific values are controlled by [country_source_map.csv](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/country_source_map.csv).

Current country files:

* [Germany first names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/first_names/germany.txt)
* [USA first names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/first_names/usa.txt)
* [UK first names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/first_names/uk.txt)
* [Canada first names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/first_names/canada.txt)
* [Germany last names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/last_names/germany.txt)
* [USA last names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/last_names/usa.txt)
* [UK last names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/last_names/uk.txt)
* [Canada last names](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/last_names/canada.txt)
* [Germany phones](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/phones/germany.txt)
* [USA phones](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/phones/usa.txt)
* [UK phones](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/phones/uk.txt)
* [Canada phones](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/phones/canada.txt)
* [Germany addresses](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/addresses/germany.txt)
* [USA addresses](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/addresses/usa.txt)
* [UK addresses](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/addresses/uk.txt)
* [Canada addresses](C:/Users/saman/IdeaProjects/python-tutorial/csv_data_generator/data/addresses/canada.txt)

To add a new country:

1. Create first-name, last-name, phone, and address files under `data/first_names/`, `data/last_names/`, `data/phones/`, and `data/addresses/`.
2. Add one row to `data/country_source_map.csv`.
3. Add the country name to `data/countries.txt`.
