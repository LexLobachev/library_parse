import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open("books.json", "r") as file:
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
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
