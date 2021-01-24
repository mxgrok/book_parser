# book_parser
### Setup
- install python3
- install requirements: `pip3 install -r requirements.txt`
- copy config_example.py as config.py
- set images and books path
- if you want to use proxies set proxies list in config.py file

### Usage
run downloader with command `python run_downloader.py -s 1 -e 20`

change args -s (end_id) and -e (end_id) as you with but  
you need to know end id must be greater than start id!

if you want to use proxies set proxies list in config.py and add one more arg: `-p true`
