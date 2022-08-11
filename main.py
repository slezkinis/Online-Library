import requests
import os
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlsplit


def check_for_redirect(response):
    if response.history != []:
        raise requests.exceptions.HTTPError()


def download_txt(response, filename, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(folder, sanitize_filename(filename))
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_image(url, directory='images/'):
    decoded_url = unquote(url)
    response = requests.get(decoded_url)
    response.raise_for_status()
    url_parts = urlsplit(decoded_url)
    path_parts = url_parts.path.split('/')
    filename = path_parts[-1]
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(directory, filename), 'wb') as file:
        file.write(response.content)



def get_book_info(id):
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    book_image = soup.find('div', class_='bookimage').find('img')['src']
    title_text = title_tag.text
    (book_title, book_author) = title_text.split('::')
    return f'{id}. {book_title.strip()}.txt', urljoin('https://tululu.org', book_image)

        
if __name__ == '__main__':
    directry = 'books'
    for book_id in range(1, 11):
        url = 'https://tululu.org/txt.php'
        params = {'id': book_id}
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            (filename, book_image_url) = get_book_info(book_id)
            download_txt(response, filename, directry)
            download_image(book_image_url)

        except requests.exceptions.HTTPError:
            pass