# book_parser
A simple python parser written just for educational purposes.

### Setup
- install python3
- install requirements:
```
pip3 install -r requirements.txt
```

- copy config_example.yml as config.yml
- set images and books path in this section:
``` yaml
storage_options:
    images_path: some you file system path
    books_path:  some you file system path
```
- if you want to use proxies set proxies list in config.yml file
``` yaml
    proxies:
        - proxy_server1:port
        - proxy_server2:port
        - proxy_server3:port
```

### Usage
run downloader with command
```
python run_downloader.py -s 1 -e 20
```

change args -s (end_id) and -e (end_id) as you with but
you need to know end id must be greater than start id!

if you want to use proxies set proxies list in config.py and add one more arg: `-p true`

Also you able to change logging level by `-l` argument:
 ```
 -l logging_level
 ```
Available logging levels:
- critical
- fatal
- error
- warning
- info
- debug


###  The purpose of the project
The code is written for educational purposes in the dvmn.org online course for web developers.