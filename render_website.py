import argparse
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload(json_path):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open(json_path, "r") as file:
        books = file.read()

    books = json.loads(books)
    chunked_books = list(chunked(books, 20))
    os.makedirs('pages', exist_ok=True)
    length_pages = len(chunked_books)

    for page, books in enumerate(chunked_books, 1):
        rendered_page = template.render(
            books=books,
            current_page=page,
            last_page=length_pages,
            pages=range(1, length_pages + 1)
        )
        with open(f'pages/index{page}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    parser = argparse.ArgumentParser(description='Где находится ваш json файл')
    parser.add_argument('--json_path', default='books.json', help='Где находится *.json файл?',
                        type=str)
    args = parser.parse_args()
    json_path = args.json_path
    on_reload(json_path)
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
