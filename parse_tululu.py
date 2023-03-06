import os
import argparse
from urllib.parse import urljoin, urlsplit
from urllib import parse
import logging
import time

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename


parser = argparse.ArgumentParser(description='С какого номера по какой парсить книги?')
parser.add_argument('start_id', nargs='?', default=1, help='С какого номера книги', type=int)
parser.add_argument('end_id', nargs='?', default=10, help='По какой номер книги', type=int)


def get_book(book_id):
    url = f'https://tululu.org/b{book_id}/'
    try:
        response = requests.get(url, allow_redirects=False)
    except requests.exceptions.ConnectionError:
        print("No internet, will try to reconnect in 10 seconds")
        time.sleep(10)
        response = requests.get(url, allow_redirects=False)
    check_for_redirect(response)
    response.raise_for_status()
    return response.text


def parse_book_page(book_html):
    soup = BeautifulSoup(book_html, 'lxml')

    books_title_tag = soup.find('td', class_='ow_px_td').find('div', id='content').find('h1')
    books_title = books_title_tag.text.split('::')
    books_title_text = books_title[0].strip()

    books_img = soup.find('div', class_='bookimage').find('img')['src']
    books_img_link = urljoin('https://tululu.org', books_img)

    books_comments_tag = soup.find('div', id='content').find_all('span', class_='black')
    books_comments = [comment.text for comment in books_comments_tag]

    books_genres_tag = soup.find('div', id='content').find('span', class_='d_book').find_all('a')
    books_genres = [genre.text for genre in books_genres_tag]

    book = {
        'books_title': books_title_text,
        'books_image': books_img_link,
        'books_comments': books_comments,
        'books_genres': books_genres
    }

    return book


def check_for_redirect(response):
    if response.status_code != 200:
        raise requests.HTTPError


def download_image(url, folder='images/'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        response = requests.get(url=url)
    except requests.exceptions.ConnectionError:
        print("No internet, will try to reconnect in 10 seconds")
        time.sleep(10)
        response = requests.get(url=url)
    response.raise_for_status()

    filename = urlsplit(parse.unquote(url)).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_txt(url, params, book_name, folder='books/'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        response = requests.get(url=url, params=params, allow_redirects=False)
    except requests.exceptions.ConnectionError:
        print("No internet, will try to reconnect in 10 seconds")
        time.sleep(10)
        response = requests.get(url=url, params=params, allow_redirects=False)
    check_for_redirect(response)
    response.raise_for_status()

    filename = f"{params['id']}. {book_name}.txt"
    filepath = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def main():
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id + 1
    url = 'https://tululu.org/txt.php'
    for book_id in range(start_id, end_id):
        params = {
            'id': book_id
        }
        try:
            book_html = get_book(book_id)
            book = parse_book_page(book_html)
            book_name = book['books_title']
            book_img = book['books_image']
            download_txt(url, params, book_name)
            download_image(book_img)
        except requests.exceptions.HTTPError:
            logging.error(f'Something went wrong with book {book_id}')


if __name__ == '__main__':
    main()
