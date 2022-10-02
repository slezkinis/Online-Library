from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server


def rebuild():
    with open('about_books.json', 'r', encoding='utf8') as file:
        books_json = file.read()
    books = json.loads(books_json)


    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        books=books
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    
    print("Site rebuilt")

rebuild()

server = Server()

server.watch('template.html', rebuild)

server.serve(root='.')