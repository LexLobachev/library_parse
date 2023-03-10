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
    check_for_redirect(response)
    response.raise_for_status()
    return response.text


def parse_book_page(book_html, url):
    soup = BeautifulSoup(book_html, 'lxml')

    book_title_tag = soup.find('td', class_='ow_px_td').find('div', id='content').find('h1')
    book_title = book_title_tag.text.split('::')
    book_title_text = book_title[0].strip()

    book_img = soup.find('div', class_='bookimage').find('img')['src']
    book_img_link = urljoin(url, book_img)

    book_comment_tags = soup.find('div', id='content').find_all('span', class_='black')
    book_comments = [comment.text for comment in book_comment_tags]

    book_genre_tags = soup.find('div', id='content').find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in book_genre_tags]

    book = {
        'book_title': book_title_text,
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


def download_txt(url, params, book_name, folder='books/'):
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url=url, params=params, allow_redirects=True)
    check_for_redirect(response)
    response.raise_for_status()

    filename = f"{params['id']}. {book_name}.txt"
    filepath = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description='?? ???????????? ???????????? ???? ?????????? ?????????????? ???????????')
    parser.add_argument('start_id', nargs='?', default=1, help='?? ???????????? ???????????? ??????????', type=int)
    parser.add_argument('end_id', nargs='?', default=10, help='???? ?????????? ?????????? ??????????', type=int)
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id + 1
    url = 'https://tululu.org/txt.php'
    for book_id in tqdm(range(start_id, end_id)):
        params = {
            'id': book_id
        }
        book_url = f'https://tululu.org/b{book_id}/'
        try:
            while True:
                try:
                    book_html = get_book(book_url)
                    break
                except requests.exceptions.ConnectionError:
                    print("No internet, will try to reconnect in 10 seconds")
                    time.sleep(10)
            book = parse_book_page(book_html, book_url)
            book_name = book['book_title']
            book_img_url = book['book_image_url']
            while True:
                try:
                    download_txt(url, params, book_name)
                    break
                except requests.exceptions.ConnectionError:
                    print("No internet, will try to reconnect in 10 seconds")
                    time.sleep(10)
            while True:
                try:
                    download_image(book_img_url)
                    break
                except requests.exceptions.ConnectionError:
                    print("No internet, will try to reconnect in 10 seconds")
                    time.sleep(10)
        except requests.exceptions.HTTPError:
            logging.error(f'Something went wrong with book {book_id}')


if __name__ == '__main__':
    main()
