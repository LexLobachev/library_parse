# Library Parser

Script for parsing [Tululu](https://tululu.org/) web-library, downloading books' covers, titles, authors & text.

## Environment

### Requirements

Python3(python 3.11 is recommended) should be already installed. Then use pip3 to install dependencies:

```bash
pip3 install -r requirements.txt
```

## Run

Launch on Linux(Python 3) or Windows:

```bash
$ python3 parse_tululu.py
```

You will parse 10 first books from site, receive images' folder with a couple of books, their ids' and titles'.

If you want to parse another range of books, just type from what book's id to what you want to parse(e.g. from 20 to
30):

```bash
$ python3 parse_tululu.py 20 30
```