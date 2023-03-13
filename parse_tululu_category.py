import os
import argparse
from urllib.parse import urljoin, urlsplit
from urllib import parse
import logging
import time

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename
from tqdm import tqdm


def get_book(url):
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    return response.text


def parse_category_page(book_html, url):
    soup = BeautifulSoup(book_html, 'lxml')

    book_id = soup.find('td', class_='ow_px_td').find('div', id='content').find('div', class_='bookimage').find('a')['href']
    book_url = urljoin(url, book_id)
    print(book_url)


def main():
    url = 'https://tululu.org/l55/'
    while True:
        try:
            book_html = get_book(url)
            break
        except requests.exceptions.ConnectionError:
            print("No internet, will try to reconnect in 10 seconds")
            time.sleep(10)
    parse_category_page(book_html, url)


if __name__ == '__main__':
    main()
