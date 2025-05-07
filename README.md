# Web Crawler App

### Description
Crawls different urls, following all `<a href>` links and prints their urls, status codes, content types, titles, and number of outgoing links into a csv file
Respects robots.txt and crawl-delay rules of each site


### Setup Instructions
Install using pip: 

* requests - for making http request
* beautifulsoup4 - for parsing html pages

Command line parameters are as follows:

```
usage: site_crawler.py [-h] [--seeds SEEDS [SEEDS ...]] [--max-pages MAX_PAGES] [--max-depth MAX_DEPTH]
                       [--rate RATE] [--allow-external] [--debug]

Crawl a set of websites

optional arguments:
  -h, --help            show this help message and exit
  --seeds SEEDS [SEEDS ...]
                        List of seed URLs to start crawling from
  --max-pages MAX_PAGES
                        Limit of pages to crawl
  --max-depth MAX_DEPTH
                        Limit of depth to crawl
  --rate RATE           How many requests/sec
  --allow-external      Allowing urls outside seeds domain
  --debug
```

Example Run Scenarios

```
python site_crawler.py --seeds https://twingdata.com --rate 0.5

python site_crawler.py --seeds https://chess.com --rate 0.5 --allow-external --max-pages 10
```
