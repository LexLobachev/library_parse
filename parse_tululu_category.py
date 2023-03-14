import os
import argparse
from urllib.parse import urljoin, urlsplit
from urllib import parse
import logging
import time
import json

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename
from tqdm import tqdm


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_book(url):
    response = requests.get(url, allow_redirects=True)
    check_for_redirect(response)
    response.raise_for_status()
    return response.text


def parse_category_page(book_html, url):
    book_ids = []
    soup = BeautifulSoup(book_html, 'lxml')

    selector = "td.ow_px_td div.bookimage"
    book_tags = soup.select(selector)
    for book in book_tags:
        book_id = book.find('a')['href']
        book_url = urljoin(url, book_id)
        print(book_url)
        book_id_number = ""
        for c in book_id:
            if c.isdigit():
                book_id_number = book_id_number + c
        book_ids.append(book_id_number)
    return book_ids


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

    filename = f"{book_id}-я книга. {book_name}.txt"
    filepath = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def create_json(title, author, img_src, book_path, comments, genres, path):
    os.makedirs(path, exist_ok=True)
    json_path = os.path.join(path, "books.json")
    all_books = []
    books = {
        "title": title,
        "author": author,
        "img_src": img_src,
        "book_path": book_path,
        "comments": comments,
        "genres": genres
    }

    if os.path.exists(json_path):
        with open(json_path) as my_file:
            all_books = json.load(my_file)

    all_books.append(books)

    with open(json_path, "w+", encoding='utf-8') as my_file:
        json.dump(all_books, my_file, ensure_ascii=False, indent=4, separators=(',', ': '))


def parse_book_page(book_html, url):
    soup = BeautifulSoup(book_html, 'lxml')

    selector = "td.ow_px_td h1"
    book_title_tag = soup.select_one(selector)
    book_title = book_title_tag.text.split('::')
    book_title_text = book_title[0].strip()

    book_author_tag = book_title_tag.find('a')
    book_author = book_author_tag.text

    book_img = soup.find('div', class_='bookimage').find('img')['src']
    book_img_link = urljoin(url, book_img)

    selector = "span.black"
    book_comment_tags = soup.select(selector)
    book_comments = [comment.text for comment in book_comment_tags]

    selector = "span.d_book a"
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


def main():
    parser = argparse.ArgumentParser(description='С какого номера страницы по какой парсить книги?')
    parser.add_argument('--start_page', default=1, help='С какого номера страницы?', type=int)
    parser.add_argument('--end_page', default=702, help='По какой номер страницы?', type=int)
    parser.add_argument('--dest_folder', default='parsed_books/', help='Где хранятся скачанные данные книг?', type=str)
    parser.add_argument('--skip_imgs', default=False, help='Не скачивать картинки?', type=bool)
    parser.add_argument('--skip_txt', default=False, help='Не скачивать книги?', type=bool)
    parser.add_argument('--json_path', default='parsed_books/', help='Куда сохранить *.json файл с результатами?',
                        type=str)
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path
    book_ids = []
    for category_page in tqdm(range(start_page, end_page)):
        url = f'https://tululu.org/l55/{category_page}'
        while True:
            try:
                book_html = get_book(url)
                break
            except requests.exceptions.ConnectionError:
                print("No internet, will try to reconnect in 10 seconds")
                time.sleep(10)
        book_ids += parse_category_page(book_html, url)
    url = 'https://tululu.org/txt.php'
    for book_id in tqdm(book_ids):
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
            book_author = book['book_author']
            book_comments = book['book_comments']
            book_genres = book['book_genres']
            if not skip_txt:
                while True:
                    try:
                        folder = os.path.join(dest_folder, 'books/')
                        book_filepath = download_txt(url, book_id, book_name, folder)
                        break
                    except requests.exceptions.ConnectionError:
                        print("No internet, will try to reconnect in 10 seconds")
                        time.sleep(10)
            else:
                book_filepath = ''
            if not skip_imgs:
                while True:
                    try:
                        folder = os.path.join(dest_folder, 'images/')
                        img_filepath = download_image(book_img_url, folder)
                        break
                    except requests.exceptions.ConnectionError:
                        print("No internet, will try to reconnect in 10 seconds")
                        time.sleep(10)
            else:
                img_filepath = ''
            while True:
                try:
                    path = json_path
                    create_json(book_name, book_author, img_filepath, book_filepath, book_comments, book_genres, path)
                    break
                except requests.exceptions.ConnectionError:
                    print("No internet, will try to reconnect in 10 seconds")
                    time.sleep(10)
        except requests.exceptions.HTTPError:
            logging.error(f'Something went wrong with book {book_id}')


if __name__ == '__main__':
    main()
