import argparse
import logging
from os.path import join
import json
import time

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import requests

from parse_tululu_book import check_for_redirect, download_image, download_txt, parse_book_page


def get_arguments():
    parser = argparse.ArgumentParser(
        'Это программа скачивает книги по страницам с сайта.'
    )
    parser.add_argument(
        '-s',
        '--start_page',
        help='Страница, с которой надо начинать скачивать книги',
        default=0,
        type=int
    )
    parser.add_argument(
        '-e',
        '--end_page',
        help='Страница, по которую надо скачивать книги',
        default=704,
        type=int
    )
    parser.add_argument(
        '-d',
        '--dest_folder',
        help='Папка с результатами',
        default=''
    )
    parser.add_argument(
        '-si',
        '--skip_imgs',
        help='Скачивать ли изображения',
        default=False
    )
    parser.add_argument(
        '-st',
        '--skip_txt',
        help='Скачивать ли книги',
        default=False
    )
    parser.add_argument(
        '-j',
        '--json_path',
        help='Где будет сохранён json-файл',
        default=''
    )
    args = parser.parse_args()
    return args


def get_urls_soups(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    book_selector = 'body .d_book'
    books_url_parts = soup.select(book_selector)
    return books_url_parts


def get_book_info(book_url):
    book_response = requests.get(book_url)
    book_response.raise_for_status()
    check_for_redirect(book_response)
    book_soup = BeautifulSoup(book_response.text, 'lxml')
    return book_soup


def get_book_url(url, url_soup):
    url_selector = 'a'
    book_url = urljoin(
        url,
        url_soup.select_one(url_selector)['href']
    )
    book_id = (
        url_soup.select_one(url_selector)['href']
        .replace('/', '').replace('b', '')
    )
    return book_url, book_id


def download_books(url_soup, args, books, url):
    book_url, book_id = get_book_url(url, url_soup)
    book_soup = get_book_info(book_url)
    parse_book = parse_book_page(book_soup, book_id)
    book_path = ''
    if not args.skip_txt:
        url = 'https://tululu.org/txt.php'
        params = {'id': book_id}
        download_response = requests.get(url, params=params)
        download_response.raise_for_status()
        check_for_redirect(download_response)
        file_name = parse_book['book_title'] + '.txt'
        download_txt(
            download_response, file_name,
            join(args.dest_folder, 'books')
        )
        book_path = join('books', file_name)
    image_path = ''
    if not args.skip_imgs:
        image_path = download_image(
            parse_book['book_image_url'],
            join(args.dest_folder, 'images')
        )
    book = {
        'title': (
            parse_book['book_title']
            .replace(' \xa0 ', '').strip()
        ),
        'author': (
            parse_book['book_author']
            .replace(' \xa0 ', '')
        ),
        'img_src': image_path,
        'book_path': book_path,
        'comments': parse_book['comments'],
        'genres': parse_book['book_genres']
    }
    books.append(book)
    return books


def main():
    books = []
    args = get_arguments()
    for number_page in range(args.start_page, args.end_page):
        while True:
            try:
                url = f'https://tululu.org/l55/{number_page}'
                urls_soups = get_urls_soups(url)
                for url_soup in urls_soups:
                    while True:
                        try:
                            books = download_books(url_soup, args, books, url)
                            break
                        except requests.HTTPError:
                            logging.warning('Книги не существует!')
                            break
                        except requests.ConnectionError:
                            logging.warning('Нет подключения к интернету!')
                            time.sleep(10)
                break
            except requests.ConnectionError:
                logging.warning('Нет подключения к интернету!')
                time.sleep(10)
            except requests.HTTPError:
                logging.warning('Книги не существует!')
                break
    Path(args.json_path).mkdir(parents=True, exist_ok=True)
    with open(
        join(args.json_path, 'about_books.json'),
        'w',
        encoding='utf8'
    ) as file:
        json.dump(books, file, ensure_ascii=False)


if __name__ == '__main__':
    main()
