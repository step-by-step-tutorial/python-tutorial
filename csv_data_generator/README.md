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
    addresses/  first_names/  job_titles/  last_names/  offices/  phones/  warehouses/
  output/
  src/
  tests/
  config.json
  config_online_shopping.json
  config_hr.json
```

`data/` is organised by kind of data, never by dataset: `first_names/`, `product_names.txt`,
`job_titles/`, and so on. A folder holds one file per key of the mapping that selects it —
`first_names/germany.txt` is keyed by country, `job_titles/engineering.txt` by department. Any
config may draw from any of these files, so a new dataset usually needs no new folders.

One config file per dataset, named `config_<dataset>.json`. Pick one with `--config`.

| Config | Output | Rows | Dataset |
| --- | --- | --- | --- |
| `config_sale.json` | `output/generated_orders.csv` | 1000 | Minimal order sample |
| `config_online_shopping.json` | `output/online_shopping_orders.csv` | 5000 | Online shopping orders |
| `config_hr.json` | `output/hr_employees.csv` | 750 | HR employee records |

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
python ./src/main.py --config ./config_sale.json
python ./src/main.py --config ./config_online_shopping.json
python ./src/main.py --config ./config_hr.json
```

Paths inside a config file are resolved relative to the folder holding that config file.

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

## Datasets

### Online Shopping — `config_online_shopping.json`

```text
order_id,order_date,sales_channel,customer_id,first_name,last_name,email,phone,
shipping_address,country,currency,warehouse,product_name,category,unit_price,quantity,
coupon_code,payment_method,shipping_method,delivery_days,order_status
```

Name, phone, address, and warehouse all follow the row's `country`, and `currency` is looked up
from it. `product_name` draws from all 10,000 catalog products, with `category` and `unit_price`
looked up from the catalog. About 40% of rows carry no coupon (`NONE`), and `Delivered` is
weighted higher than other statuses by repeating it in `order_statuses.txt`.

### HR — `config_hr.json`

```text
employee_id,first_name,last_name,work_email,phone,home_address,country,office,timezone,
department,job_title,seniority_level,salary_grade,base_salary_usd,bonus_percent,
employment_type,work_mode,employment_status,hire_date,performance_rating,manager_id
```

`job_title` is drawn from the file mapped to the row's `department`, so titles never leak across
departments. `office` and `timezone` follow `country`; `salary_grade` and `base_salary_usd` are
looked up from `seniority_level`. `seniority_level`, `employment_type`, and `job_title` are drawn
independently, so combinations such as a Junior Software Architect do occur — map the level or the
title through a mapping file if a dataset needs those to agree.

## Data Files

| File | Contents |
| --- | --- |
| `data/countries.txt` | Countries wired up in the mapping files (Germany, USA, UK, Canada) |
| `data/countries_iso.txt` | All 249 ISO 3166-1 country names, for configs that do not need per-country source files |
| `data/country_source_map.csv` | Per-country first name, last name, phone, and address files |
| `data/country_profile_map.csv` | Per-country `currency_code` and `timezone` |
| `data/product_names.txt` | Product pool the `product_name` column draws from (all 10,000 catalog products) |
| `data/product_catalog.csv` | 10,000 products with `category` and `unit_price`, keyed by `product` |
| `data/first_names/*.txt`, `data/last_names/*.txt` | First and last names per country |
| `data/phones/*.txt`, `data/addresses/*.txt` | Phone numbers and addresses per country |
| `data/sales_channels.txt` | Web Store, iOS App, Marketplace, ... |
| `data/payment_methods.txt` | Credit Card, PayPal, Klarna, ... |
| `data/shipping_methods.txt` | Standard, Express, Pickup Point, ... |
| `data/order_statuses.txt` | Order lifecycle states, `Delivered` weighted |
| `data/coupon_codes.txt` | Coupon codes plus repeated `NONE` entries |
| `data/country_warehouse_map.csv` | Country to warehouse file |
| `data/warehouses/*.txt` | Warehouses per country |
| `data/departments.txt` | 10 departments |
| `data/department_job_map.csv` | Department to job title file |
| `data/job_titles/*.txt` | Job titles per department |
| `data/seniority_levels.txt` | Intern through Director |
| `data/salary_bands.csv` | Seniority level to `salary_grade` and `base_salary_usd` |
| `data/employment_types.txt` | Full-time, Contract, Internship, ... |
| `data/work_modes.txt` | On-site, Hybrid, Remote |
| `data/employment_statuses.txt` | Active, Probation, Notice Period, ... |
| `data/country_office_map.csv` | Country to office file |
| `data/offices/*.txt` | Offices per country |