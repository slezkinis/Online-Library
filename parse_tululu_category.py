from pprint import pprint
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from main import check_for_redirect, download_image, download_txt
from os.path import join
import json
import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
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
    args = parser.parse_args()
    return args.start_page, args.end_page


if __name__ == '__main__':
    about_books = []
    start_page, end_page = get_arguments()
    for number_page in range(start_page, end_page):
        url = f'https://tululu.org/l55/{number_page}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_selector = 'body .d_book'
        books_url_parts = soup.select(book_selector)
        for url_part in books_url_parts:
            try:
                url_selector = 'a'
                book_url = urljoin(
                    url,
                    url_part.select_one(url_selector)['href']
                )
                print(book_url)
                book_id = (url_part.select_one(url_selector)['href']).replace('/', '').replace('b', '')
                book_response = requests.get(book_url)
                check_for_redirect(book_response)
                book_soup = BeautifulSoup(book_response.text, 'lxml')
                title_selector = 'h1'
                title_tag = book_soup.select_one(title_selector)
                img_selector = '.bookimage img'
                book_image = book_soup.select_one(img_selector)['src']
                title_text = title_tag.text
                book_title, book_author = title_text.split('::')
                book_title = book_title.strip()
                
                url = 'https://tululu.org/txt.php'
                params = {'id': book_id}
                download_response = requests.get(url, params=params)
                download_response.raise_for_status()
                file_name = f'{book_title}.txt'
                download_txt(download_response, file_name, 'books')
                book_path = join('books', file_name)
                image_path = download_image(urljoin(book_url, book_image))
                genres_selector = 'span.d_book a'
                genres_tags = book_soup.select(genres_selector)
                genres_texts = [genre_tag.text for genre_tag in genres_tags]
                comments_selector = 'div.texts span.black'
                comments_tags = book_soup.select(comments_selector)
                comments_texts = [
                    comment_tag.text
                    for comment_tag in comments_tags
                ]
                about_book = {
                    'title': book_title.replace(' \xa0 ', '').strip(),
                    'author': book_author.replace(' \xa0 ', ''),
                    'img_src': image_path,
                    'book_path': book_path,
                    'comments': comments_texts,
                    'genres': genres_texts
                }
                about_books.append(about_book)
            except requests.exceptions.HTTPError:
                continue
    with open("about_books.json", "w", encoding='utf8') as my_file:
        json.dump(about_books, my_file, ensure_ascii=False)
