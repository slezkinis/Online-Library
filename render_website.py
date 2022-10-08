from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server
from more_itertools import chunked
from pathlib import Path
from math import ceil


def rebuild():
    Path('pages').mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
        )
    template = env.get_template('template.html')
    with open('about_books.json', 'r', encoding='utf8') as file:
        books_json = file.read()
    books = json.loads(books_json)
    pages = list(chunked(books, 10))
    pages_number = ceil(len(books) / 10)
    for page_number, page_books in enumerate(pages):
        split_books = list(chunked(page_books, 10))
        rendered_page = template.render(
            split_books=split_books, 
            pages_number=pages_number,
            page_number=page_number + 1
        )
        with open(f'pages/index_{page_number + 1}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
        
    print("Site rebuilt")

rebuild()

server = Server()

server.watch('template.html', rebuild)

server.serve(root='pages')