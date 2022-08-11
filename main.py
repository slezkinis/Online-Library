import requests
import os
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history != []:
        raise requests.exceptions.HTTPError()


def download_txt(response, filename, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(folder, sanitize_filename(filename))
    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_name(id):
    url = f'https://tululu.org/read{id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    title_text = title_tag.text
    (book_title, book_author) = title_text.split('::')
    return f'{id}. {book_title.strip()}.txt'

        
if __name__ == '__main__':
    directry = 'books'
    for book_id in range(1, 11):
        url = 'https://tululu.org/txt.php'
        params = {'id': book_id}
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            filename = get_name(book_id)
            download_txt(response, filename, directry)
        except requests.exceptions.HTTPError:
            pass