import requests
import os
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote, urlsplit
import argparse
import time
import logging


def check_for_redirect(response):
    if response.history:
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
    check_for_redirect(response)
    url_parts = urlsplit(decoded_url)
    path_parts = url_parts.path.split('/')
    filename = path_parts[-1]
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(directory, filename), 'wb') as file:
        file.write(response.content)


def download_comments(comments, file_name, directory):
    Path(directory).mkdir(parents=True, exist_ok=True)
    if comments:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'a', encoding='UTF-8') as file:
            [file.write(f'{comment}\n') for comment in comments]


def parse_book_page(soup):
    comments_tags = soup.find_all('div', class_='texts')
    comments_texts = [
        comment_tag.find('span', class_='black').text
        for comment_tag in comments_tags
        ]

    title_tag = soup.find('h1')
    book_image = soup.find('div', class_='bookimage').find('img')['src']
    title_text = title_tag.text
    book_title, book_author = title_text.split('::')

    genre_field = soup.find('span', class_='d_book')
    genres_tags = genre_field.find_all('a')
    genres_texts = [genre_tag.text for genre_tag in genres_tags]
    book_url = 'https://tululu.org/txt.php'
    about_book = {
        'book_genres': genres_texts,
        'book_image_url': urljoin(
            book_url,
            book_image
            ),
        'book_author': book_author.strip(),
        'book_title': book_title.strip(),
        'comments': comments_texts
    }
    return about_book


def get_arguments():
    parser = argparse.ArgumentParser()
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
    start_id = args.start_id
    end_id = args.end_id + 1
    return start_id, end_id


def get_soup(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def print_about_book(about_book):
    print(f'Название: {about_book["book_title"]}')
    print(f'Автор: {about_book["book_author"]}')
    print()


def get_download_response(book_id):
    url = 'https://tululu.org/txt.php'
    params = {'id': book_id}
    download_response = requests.get(url, params=params)
    download_response.raise_for_status()
    return download_response


def main():
    start_id, end_id = get_arguments()
    for book_id in range(start_id, end_id):
        while True:
            try:
                download_response = get_download_response(book_id)
                try:
                    check_for_redirect(download_response)
                    soup = get_soup(book_id)
                    about_book = parse_book_page(soup)
                    download_txt(
                        download_response,
                        f'{book_id}. {about_book["book_title"]}.txt',
                        'books'
                        )
                    download_image(about_book['book_image_url'])
                    download_comments(
                        about_book['comments'],
                        f'{book_id}. {about_book["book_title"]}.txt',
                        'comments'
                    )
                    print_about_book(about_book)
                    break
                except requests.exceptions.HTTPError:
                    logging.warning(f'Книги №{book_id} не найдена!')
                    print()
                    break
            except requests.ConnectionError:
                logging.warning('Нет подключения к интернету! Через 10 сек. повториться попытка')
                print()
                time.sleep(10)



if __name__ == '__main__':
    main()