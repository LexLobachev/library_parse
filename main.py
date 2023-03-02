import os
from urllib.parse import urljoin, urlsplit
from urllib import parse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath, sanitize_filename


def get_book_name(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')

    books_title_tag = soup.find('td', class_='ow_px_td').find('div', id='content').find('h1')
    books_title = books_title_tag.text.split('::')
    books_title_text = books_title[0].strip()
    print('Заголовок:', books_title_text)
    books_img = soup.find('div', class_='bookimage').find('img')['src']
    books_img_link = urljoin('https://tululu.org', books_img)
    books_comments_tag = soup.find('div', id='content').find_all('span', class_='black')
    books_comments = [comment.text for comment in books_comments_tag]
    books_genres_tag = soup.find('div', id='content').find('span', class_='d_book').find_all('a')
    books_genres = [genre.text for genre in books_genres_tag]
    print(books_genres)

    return books_title_text, books_img_link, books_comments, books_genres


def check_for_redirect(response):
    if response.status_code != 200:
        raise requests.HTTPError


def download_image(url, folder='images/'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url=url)
    response.raise_for_status()

    filename = urlsplit(parse.unquote(url)).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_txt(url, params, folder='books/'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url=url, params=params, allow_redirects=False)
    check_for_redirect(response)
    response.raise_for_status()
    book_name, book_img, book_comments, book_genres = get_book_name(params['id'])
    download_image(book_img)

    filename = f"{params['id']}. {book_name}.txt"
    filepath = sanitize_filepath(os.path.join(folder, sanitize_filename(filename)))
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def main():
    url = 'https://tululu.org/txt.php'
    params = {
        'id': 1
    }
    for book_id in range(1, 11):
        try:
            download_txt(url, params)
        except requests.exceptions.HTTPError:
            pass
        params['id'] += 1


if __name__ == '__main__':
    main()
