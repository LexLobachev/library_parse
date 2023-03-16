import os
import argparse
from urllib.parse import urljoin
import logging
import time
import json

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from parse_tululu import get_page_html, download_image, download_txt, parse_book_page


def parse_category_page(book_html, url):
    book_ids = []
    soup = BeautifulSoup(book_html, 'lxml')

    selector = "td.ow_px_td div.bookimage"
    book_tags = soup.select(selector)
    for book in book_tags:
        book_id = book.find('a')['href']
        book_id_number = book_id.replace('/', '').replace('b', '')
        book_ids.append(book_id_number)

    return book_ids


def create_json(all_books, path):
    os.makedirs(path, exist_ok=True)
    json_path = os.path.join(path, "books.json")

    with open(json_path, "w+", encoding='utf-8') as file:
        json.dump(all_books, file, ensure_ascii=False, indent=4, separators=(',', ': '))


def main():
    parser = argparse.ArgumentParser(description='С какого номера страницы по какой парсить книги?')
    parser.add_argument('--start_page', default=1, help='С какого номера страницы?', type=int)
    parser.add_argument('--end_page', default=702, help='По какой номер страницы?', type=int)
    parser.add_argument('--dest_folder', default='parsed_books/', help='Где хранятся скачанные данные книг?', type=str)
    parser.add_argument('--skip_imgs', help='Не скачивать картинки?', action='store_true')
    parser.add_argument('--skip_txt', help='Не скачивать книги?', action='store_true')
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
                category_html = get_page_html(url)
                break
            except requests.exceptions.ConnectionError:
                print("No internet, will try to reconnect in 10 seconds")
                time.sleep(10)
        book_ids += parse_category_page(category_html, url)
    url = 'https://tululu.org/txt.php'
    parsed_books = []
    for book_id in tqdm(book_ids):
        book_url = f'https://tululu.org/b{book_id}/'
        try:
            while True:
                try:
                    book_html = get_page_html(book_url)
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

            book = {
                "title": book_name,
                "author": book_author,
                "img_src": img_filepath,
                "book_path": book_filepath,
                "comments": book_comments,
                "genres": book_genres
            }
            parsed_books.append(book)
        except requests.exceptions.HTTPError:
            logging.error(f'Something went wrong with book {book_id}')
    create_json(parsed_books, json_path)


if __name__ == '__main__':
    main()
