import argparse
import logging
import os
import time
from urllib import parse
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from tqdm import tqdm


def get_page_html(url):
    response = requests.get(url, allow_redirects=True)
    check_for_redirect(response)
    response.raise_for_status()
    return response.text


def parse_book_page(book_html, url):
    soup = BeautifulSoup(book_html, 'lxml')

    selector = 'td.ow_px_td h1'
    book_title_tag = soup.select_one(selector)
    book_title = book_title_tag.text.split('::')
    book_title_text = book_title[0].strip()

    book_author_tag = book_title_tag.find('a')
    book_author = book_author_tag.text

    selector = 'div.bookimage img[src]'
    book_img = soup.select_one(selector)['src']
    book_img_link = urljoin(url, book_img)
    selector = '#content span.black'
    book_comment_tags = soup.select(selector)
    book_comments = [comment.text for comment in book_comment_tags]

    selector = 'span.d_book a'
    book_genre_tags = soup.select(selector)
    book_genres = [genre.text for genre in book_genre_tags]

    book = {
        'book_title': book_title_text,
        'book_author': book_author,
        'book_image_url': book_img_link,
        'book_comments': book_comments,
        'book_genres': book_genres
    }

    return book


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_image(url, folder='images/'):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url=url)
    response.raise_for_status()

    filename = urlsplit(parse.unquote(url)).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def download_txt(url, book_id, book_name, folder='books/'):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url=url, params={'id': book_id}, allow_redirects=True)
    check_for_redirect(response)
    response.raise_for_status()

    book_name = book_name.replace(' ', '_')
    filename = f"{book_id}.{book_name}.txt"
    filepath = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description='С какого номера по какой парсить книги?')
    parser.add_argument('start_id', nargs='?', default=1, help='С какого номера книги', type=int)
    parser.add_argument('end_id', nargs='?', default=10, help='По какой номер книги', type=int)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id + 1
    url = 'https://tululu.org/txt.php'
    for book_id in tqdm(range(start_id, end_id)):
        book_url = f'https://tululu.org/b{book_id}/'
        try:
            while True:
                try:
                    book_html = get_page_html(book_url)
                    break
                except requests.exceptions.ConnectionError:
                    print('No internet, will try to reconnect in 10 seconds')
                    time.sleep(10)
            book = parse_book_page(book_html, book_url)
            book_name = book['book_title']
            book_img_url = book['book_image_url']
            while True:
                try:
                    download_txt(url, book_id, book_name)
                    break
                except requests.exceptions.ConnectionError:
                    print('No internet, will try to reconnect in 10 seconds')
                    time.sleep(10)
            while True:
                try:
                    download_image(book_img_url)
                    break
                except requests.exceptions.ConnectionError:
                    print('No internet, will try to reconnect in 10 seconds')
                    time.sleep(10)
        except requests.exceptions.HTTPError:
            logging.error(f'Something went wrong with book {book_id}')


if __name__ == '__main__':
    main()
