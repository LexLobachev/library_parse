# Library Parser

Script for parsing [Tululu](https://tululu.org/) web-library, downloading books' covers, titles, authors & text.

Working site is available at the [link](https://lexlobachev.github.io/library_parse/)

## Environment

### Requirements

Python3(python 3.11 is recommended) should be already installed. Then use pip3 to install dependencies:

```bash
pip3 install -r requirements.txt
```

## Run

Launch on Linux(Python 3) or Windows:

### parse_tululu.py

```bash
$ python3 parse_tululu.py
```

You will parse 10 first books from site, receive images' folder with a couple of books, their ids' and titles'.

If you want to parse another range of books, just type from what book's id to what you want to parse(e.g. from 20 to
30):

```bash
$ python3 parse_tululu.py 20 30
```

### parse_tululu_category.py

```bash
$ python3 parse_tululu_category.py
```

You will parse all books from site in category `фантастика`, receive parsed_books' with images' folder, folder with
books, and json file with more info about parsed books.

If you want to parse another range of pages, just type from what page to what you want to parse(e.g. only 700):

```bash
$ python3 parse_tululu_category.py --start_page 700 --end_page 701
```

If you don't want to parse images or books, just type `--skip_imgs` and `skip_txt` respectively:

```bash
$ python3 parse_tululu_category.py --skip_imgs --skip_txt
```

If you want to change the destination folder for all parsed information, just type `--dest_folder YOUR_DEST`(e.g. `--dest_folder some_folder`):

```bash
$ python3 parse_tululu_category.py --dest_folder some_folder
```

If you want to change `*.json` filepath, just type `--json_path `(e.g. `--dest_folder some_path`):

```bash
$ python3 parse_tululu_category.py --json_path some_path
```

### render_website.py

```bash
$ python3 render_website.py
```

If you want to change `*.json` filepath, just type `--json_path `(e.g. `--dest_folder some_path`):

```bash
$ python3 render_website.py --json_path some_path
```

