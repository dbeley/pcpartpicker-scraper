# pcpartpicker-scraper

Scraper for pcpartpicker.com

## Requirements

- bs4
- lxml
- numpy
- pandas
- requests
- selenium
- tqdm

## Installation of the virtualenv (recommended)

```
pipenv install
```

## Usage

```
python get_builds_urls.py
python builds-scraper.py -f FILE_BUILDS_URLS

python get_parts_urls.py
python parts-scraper.py -f FILE_PARTS_URLS
```

## Help

```
python get_builds_urls.py -h
python builds-scraper.py -h

python get_parts_urls.py -h
python parts-scraper.py -h
```
