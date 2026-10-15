<h1 align="center">Geodata Platform</h1>

Builds one CSV of real street addresses per target city from [Overture Maps](https://overturemaps.org/) address
data, enriched with city information (GeoNames id, timezone, population) from [GeoNames](https://www.geonames.org/).
The output is the address source that `test_data_platform` uses to generate realistic house data.

```text
Geodata Platform
    load GeoNames populated places and postal codes for the target states
    read the Overture addresses of each target (Parquet)
    keep the addresses in the target country, state and cities
    enrich them with GeoNames city data
    write output/<city>.csv
```

## Project Structure

```text
geodata_platform
├── config/targets.json          targets and input/output files
├── data/                        downloaded input files (not committed)
├── output/                      generated CSV files (not committed)
├── src/geodata_platform
│   ├── main.py                  command line entry point
│   ├── model.py                 data models: target, pipeline config, GeoNames place, postal code, Overture address, output address
│   ├── geo_data_repository.py   GeoNames places and postal codes, read once from the dumps
│   ├── address_matcher.py       matches Overture addresses to a target and builds output records
│   ├── pipeline.py              reads Parquet, matches addresses, writes CSV
│   └── util/                    text, geometry, file (JSON, TSV, CSV) and Parquet helpers
└── tests
```

All commands below run from the repository root.

## 1. Prerequisite

* Python 3.10+
* `curl` and `unzip` for the GeoNames downloads

```shell
python --version
pip --version
```

## 2. Install

```shell
python -m pip install --upgrade pip
pip install -r ./geodata_platform/requirements.txt
pip install -e ./geodata_platform
```

## 3. Download Input Data

All input files go to `./geodata_platform/data`.

### 3.1. GeoNames

Download from [GeoNames](https://www.geonames.org/export/):

* [All Countries (places)](https://download.geonames.org/export/dump/allCountries.zip), saved as `allCountries.txt`
* [All Countries (postal codes)](https://download.geonames.org/export/zip/allCountries.zip), saved as
  `postalCodes_allCountries.txt`

Both archives contain a file named `allCountries.txt`, so the postal codes are extracted under another name:

```shell
mkdir -p ./geodata_platform/data
curl -L -o ./geodata_platform/data/places.zip https://download.geonames.org/export/dump/allCountries.zip
curl -L -o ./geodata_platform/data/postal_codes.zip https://download.geonames.org/export/zip/allCountries.zip
unzip -p ./geodata_platform/data/places.zip allCountries.txt > ./geodata_platform/data/allCountries.txt
unzip -p ./geodata_platform/data/postal_codes.zip allCountries.txt > ./geodata_platform/data/postalCodes_allCountries.txt
rm ./geodata_platform/data/places.zip ./geodata_platform/data/postal_codes.zip
```

### 3.2. Overture Maps

Download the address data of each target city with the
[overturemaps CLI](https://docs.overturemaps.org/getting-data/), installed by `requirements.txt`:

```shell
# Los Angeles
overturemaps download \
  --bbox=-118.70,33.70,-117.60,34.35 \
  --type=address \
  -f geoparquet \
  -o ./geodata_platform/data/overture_los_angeles_addresses.parquet

# New York
overturemaps download \
  --bbox=-74.30,40.45,-73.65,40.95 \
  --type=address \
  -f geoparquet \
  -o ./geodata_platform/data/overture_nyc_addresses.parquet
```

## 4. Configure

Targets are configured in [config/targets.json](config/targets.json): country, state, cities, the Overture input
file and the output file name. Relative paths are resolved against the config file's directory. To add a city,
download its Overture addresses (step 3.2) and add a target.

## 5. Test

The tests use small generated fixture files, so they do not need the downloads.

```shell
pytest ./geodata_platform
```

## 6. Run

```shell
python -m geodata_platform.main --config ./geodata_platform/config/targets.json
```

The CSV files are written to `./geodata_platform/output`. A target whose input file is missing is skipped with a
warning.

## 7. Use the Output in test_data_platform

```shell
cp ./geodata_platform/output/los_angeles.csv ./test_data_platform/data/los_angeles.csv
```

## 8. Clean

```shell
rm -rf ./geodata_platform/output
rm -rf ./geodata_platform/src/*.egg-info
```
