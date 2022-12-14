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
        books = json.load(file)
    page_length = 10
    pages = list(chunked(books, page_length))
    pages_number = ceil(len(books) / page_length)
    for page_number, page_books in enumerate(pages, start=1):
        split_books = list(chunked(page_books, page_length))
        rendered_page = template.render(
            split_books=split_books, 
            pages_number=pages_number,
            page_number=page_number
        )
        with open(f'pages/index_{page_number}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)
        
    print("Site rebuilt")


def main():
    rebuild()
    
    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')


if __name__ == '__main__':
    main()