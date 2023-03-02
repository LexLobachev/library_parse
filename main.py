import requests
import os
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

    return book_title_text


def check_for_redirect(response):
    if response.status_code != 200:
        raise requests.HTTPError


def download_txt(url, params, folder='books/'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url=url, params=params, allow_redirects=False)
    check_for_redirect(response)
    response.raise_for_status()
    book_name = get_book_name(params['id'])

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
