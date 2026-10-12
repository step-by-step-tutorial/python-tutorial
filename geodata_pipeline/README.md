# Geodata Pipeline

Builds one CSV of real street addresses per target city from [Overture Maps](https://overturemaps.org/) address
data, enriched with city information (GeoNames id, timezone, population) from [GeoNames](https://www.geonames.org/).
The output is the address source that `test_data` uses to generate realistic house data.

```text
Geodata Pipeline
    load GeoNames populated places and postal codes for the target states
    read the Overture addresses of each target (Parquet)
    keep the addresses in the target country, state and cities
    enrich them with GeoNames city data
    write output/<city>.csv
```

## Project Structure

```text
geodata_pipeline
├── config/targets.json          targets and input/output files
├── data/                        downloaded input files (not committed)
├── output/                      generated CSV files (not committed)
├── src/geodata_pipeline
│   ├── cli.py                   command line entry point
│   ├── config.py                Target, PipelineConfig
│   ├── model.py                 GeoNames, postal code, Overture address and output records
│   ├── repository.py            GeoNames places and postal codes, read once from the dumps
│   ├── matcher.py               matches Overture addresses to a target and builds output records
│   ├── pipeline.py              reads Parquet, matches addresses, writes CSV
│   └── util/                    text, geometry and file helpers
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
pip install -r ./geodata_pipeline/requirements.txt
pip install -e ./geodata_pipeline
```

## 3. Download Input Data

All input files go to `./geodata_pipeline/data`.

### 3.1. GeoNames

Download from [GeoNames](https://www.geonames.org/export/):

* [All Countries (places)](https://download.geonames.org/export/dump/allCountries.zip), saved as `allCountries.txt`
* [All Countries (postal codes)](https://download.geonames.org/export/zip/allCountries.zip), saved as
  `postalCodes_allCountries.txt`

Both archives contain a file named `allCountries.txt`, so the postal codes are extracted under another name:

```shell
mkdir -p ./geodata_pipeline/data
curl -L -o ./geodata_pipeline/data/places.zip https://download.geonames.org/export/dump/allCountries.zip
curl -L -o ./geodata_pipeline/data/postal_codes.zip https://download.geonames.org/export/zip/allCountries.zip
unzip -p ./geodata_pipeline/data/places.zip allCountries.txt > ./geodata_pipeline/data/allCountries.txt
unzip -p ./geodata_pipeline/data/postal_codes.zip allCountries.txt > ./geodata_pipeline/data/postalCodes_allCountries.txt
rm ./geodata_pipeline/data/places.zip ./geodata_pipeline/data/postal_codes.zip
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
  -o ./geodata_pipeline/data/overture_los_angeles_addresses.parquet

# New York
overturemaps download \
  --bbox=-74.30,40.45,-73.65,40.95 \
  --type=address \
  -f geoparquet \
  -o ./geodata_pipeline/data/overture_nyc_addresses.parquet
```

## 4. Configure

Targets are configured in [config/targets.json](config/targets.json): country, state, cities, the Overture input
file and the output file name. Relative paths are resolved against the config file's directory. To add a city,
download its Overture addresses (step 3.2) and add a target.

## 5. Run

```shell
python -m geodata_pipeline --config ./geodata_pipeline/config/targets.json
```

The CSV files are written to `./geodata_pipeline/output`. A target whose input file is missing is skipped with a
warning.

## 6. Use the Output in test_data

```shell
cp ./geodata_pipeline/output/los_angeles.csv ./test_data/data/los_angeles.csv
```

## 7. Test

The tests use small generated fixture files, so they do not need the downloads.

```shell
pytest ./geodata_pipeline
```

## 8. Clean

```shell
rm -rf ./geodata_pipeline/output
rm -rf ./geodata_pipeline/src/*.egg-info
```
