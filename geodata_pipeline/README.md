# Geodata Pipeline

Builds one CSV of real street addresses per target city from [Overture Maps](https://overturemaps.org/) address
data, enriched with city information (GeoNames id, timezone, population) from [GeoNames](https://www.geonames.org/).
The output is the address source that `test_data` uses to generate realistic house data
(`test_data/data/los_angeles.csv`).

```text
Geodata Pipeline
    load GeoNames populated places and postal codes for the target states
    read Overture addresses of each target (Parquet)
    keep addresses in the target country, state and cities
    enrich with GeoNames city data
    write output/<city>.csv
```

Targets (country, state, cities, input and output files) are configured in [config/targets.json](config/targets.json).
Relative paths in the config are resolved against the config file's directory.

## Prerequisite

* Python

## Prepare Environment

```shell
python --version
pip --version
python -m pip install --upgrade pip
pip install -r ./geodata_pipeline/requirements.txt
pip install -e ./geodata_pipeline
```

## Test

```shell
cd ./geodata_pipeline
pytest
```

## Download

All input files go to `./geodata_pipeline/data`.

From [GeoNames](https://www.geonames.org/export/):

* [All Countries (places)](https://download.geonames.org/export/dump/allCountries.zip), unzipped as `allCountries.txt`
* [All Countries (postal codes)](https://download.geonames.org/export/zip/allCountries.zip), unzipped as
  `postalCodes_allCountries.txt`. This archive also contains a file named `allCountries.txt`, so rename it to avoid
  overwriting the places file.

```shell
cd ./geodata_pipeline
mkdir -p data
curl -L -o data/places.zip https://download.geonames.org/export/dump/allCountries.zip
curl -L -o data/postal_codes.zip https://download.geonames.org/export/zip/allCountries.zip
unzip -p data/places.zip allCountries.txt > data/allCountries.txt
unzip -p data/postal_codes.zip allCountries.txt > data/postalCodes_allCountries.txt
rm data/places.zip data/postal_codes.zip
```

From [Overture Maps](https://docs.overturemaps.org/getting-data/), using the `overturemaps` CLI:

```shell
cd ./geodata_pipeline

## Los Angeles
overturemaps download \
  --bbox=-118.70,33.70,-117.60,34.35 \
  --type=address \
  -f geoparquet \
  -o data/overture_los_angeles_addresses.parquet

## New York
overturemaps download \
  --bbox=-74.30,40.45,-73.65,40.95 \
  --type=address \
  -f geoparquet \
  -o data/overture_nyc_addresses.parquet
```

## Run

```shell
cd ./geodata_pipeline
python -m geodata_pipeline --config ./config/targets.json
```

The CSV files are written to `./geodata_pipeline/output`. To use a new address file in `test_data`, copy it to
`./test_data/data`:

```shell
cp ./geodata_pipeline/output/los_angeles.csv ./test_data/data/los_angeles.csv
```

## Clean Directory

```shell
rm -rf ./geodata_pipeline/output
rm -rf ./geodata_pipeline/src/*.egg-info
```
