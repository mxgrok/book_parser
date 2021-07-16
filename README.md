# book_parser
A simple python parser written just for educational purposes.

### Setup
- install python3
- install requirements:
```
pip3 install -r requirements.txt
```

### Usage
- If you want to download all books, then you can do it using the script: `run_downloader.py`
run script with command:
```
python run_downloader.py -s 1 -e 20
```
where `-s (start_id)` and `-e (end_id)` is begin and end sequence book numbers

change args -s (start_id) and -e (end_id) as you wish, but
you need to know end id must be greater than start id!

- If you want to download all books from the SciFi(Science Fiction) category , then you can do it using the script: `parse_tululu_category.py`
run script with command:
```
python parse_tululu_category.py -sp 1 -ep 20
```
where `-sp (start_page)` and `-ep (end_page)` is begin and end sequence of pagination numbers

change args -sp (start_page) and -ep (end_page) as you wish, but
you need to know end id must be greater than start id!

### Other downloading options:
- `-d`, `--dest_folder`- Path to the directory with the parsing results
- `-j`, `--json_path` - Specify your path to * .json file with results
- `-si`, `--skip_imgs` - Do not download images
- `-st`, `--skip_txt` - Do not download text

###  The purpose of the project
The code is written for educational purposes in the dvmn.org online course for web developers.
