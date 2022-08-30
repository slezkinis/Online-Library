import requests
import os
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlsplit
from pprint import pprint
import argparse


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
    

def parse_book_page(soup):
    about_book = {}
    comments_tags = soup.find_all('div', class_='texts')
    comments_texts = []
    for comment_tag in comments_tags:
        comment_text_tag = comment_tag.find('span', class_='black')
        comments_texts.append(comment_text_tag.text)
    about_book['comments'] = comments_texts

    title_tag = soup.find('h1')
    book_image = soup.find('div', class_='bookimage').find('img')['src']
    title_text = title_tag.text
    (book_title, book_author) = title_text.split('::')
    about_book['book_title'] = book_title.strip()
    about_book['book_author'] = book_author.strip()
    about_book['book_image_url'] = urljoin('https://tululu.org', book_image)

    genre_field = soup.find('span', class_='d_book')
    genres_tags = genre_field.find_all('a')
    genres_texts = []
    for genre_tag in genres_tags:
        genre_text = genre_tag.text
        genres_texts.append(genre_text)
    about_book['book_genres'] = genres_texts
    return about_book

     
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description='Описание что делает программа'
    )
    parser.add_argument(
        '-s',
        '--start_id',
        help='ID книги, с которой надо скачивать',
        default=1,
        type=int
    )
    parser.add_argument(
        '-e',
        '--end_id',
        help='ID книги, по которой надо скачивать', 
        default=10,
        type=int
    )
    args = parser.parse_args()
    for book_id in range(
                        args.start_id,
                        args.end_id + 1
                        ):
        url = 'https://tululu.org/txt.php'
        params = {'id': book_id}
        download_response = requests.get(url, params=params)
        try:
            download_response.raise_for_status()
            check_for_redirect(download_response)
            url = f'https://tululu.org/b{book_id}/'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            about_book = parse_book_page(soup)
            download_txt(
                download_response,
                f'{book_id}. {about_book["book_title"]}.txt',
                'books'
                )
            download_image(about_book['book_image_url'])
            print(f'Название: {about_book["book_title"]}')
            print(f'Автор: {about_book["book_author"]}')
            print()
        except requests.exceptions.HTTPError:
            pass