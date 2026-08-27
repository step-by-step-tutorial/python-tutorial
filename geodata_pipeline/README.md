
## Download

* From [www.geonames.org](https://www.geonames.org/export/):
  * [All Countries (Country, State, City)](https://download.geonames.org/export/dump/allCountries.zip)
  * [Country Info](https://download.geonames.org/export/dump/countryInfo.txt)
  * [Admin1 Codes ASCII](https://download.geonames.org/export/dump/admin1CodesASCII.txt)
  * [All Countries (Postal code)](https://download.geonames.org/export/zip/allCountries.zip)


* From [[www.overturemaps.org](https://overturemaps.org/)](https://docs.overturemaps.org/getting-data/)

```shell
## Install Python and PIP
python --version
pip --version

## Install packages and prepare environment
pip install overturemaps
mkdir data

## Los Angeles
overturemaps download \
  --bbox=-118.70,33.70,-117.60,34.35 \
  --type=address \
  -f geoparquet \
  -o data/overture_los_angeles_addresses.parquet

overturemaps download \
  --bbox=-118.70,33.70,-117.60,34.35 \
  --type=place \
  -f geoparquet \
  -o data/overture_los_angeles_places.parquet
  
## New York
overturemaps download \
  --bbox=-74.30,40.45,-73.65,40.95 \
  --type=address \
  -f geoparquet \
  -o data/overture_nyc_addresses.parquet

overturemaps download \
  --bbox=-74.30,40.45,-73.65,40.95 \
  --type=place \
  -f geoparquet \
  -o data/overture_nyc_places.parquet
```

```shell
python ./geodata_pipeline/pipeline.py
```