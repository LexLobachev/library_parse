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

    book_descriptions = json.load(open(json_path))
    chunked_book_descriptions = list(chunked(book_descriptions, 10))
    os.makedirs('pages', exist_ok=True)
    total_pages_number = len(chunked_book_descriptions)

    for page, book_descriptions in enumerate(chunked_book_descriptions, 1):
        rendered_page = template.render(
            book_descriptions=book_descriptions,
            current_page=page,
            last_page=total_pages_number,
            pages=range(1, total_pages_number + 1)
        )
        with open(f'pages/index{page}.html', 'w', encoding='utf8') as file:
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
