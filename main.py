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

    book_tag = soup.find('td', class_='ow_px_td').find('div', id='content').find('h1')
    book_title = book_tag.text.split('::')
    book_title_text = book_title[0].strip()
    print(book_title_text)
    book_img = soup.find('div', class_='bookimage').find('img')['src']
    book_img_link = urljoin('https://tululu.org', book_img)
    book_comments_tag = soup.find('div', id='content').find_all('span', class_='black')
    book_comments = [comment.text for comment in book_comments_tag]
    for comment in book_comments:
        print(comment)

    return book_title_text, book_img_link, book_comments


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
    book_name, book_img, book_comments = get_book_name(params['id'])
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
    # download_image("https://tululu.org/shots/10.jpg")
