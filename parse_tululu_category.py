from pprint import pprint
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from main import check_for_redirect, download_image, download_txt
from os.path import join
import json




if __name__ == '__main__':
    about_books = []
    for number_page in range(1, 2):
        url = f'https://tululu.org/l55/{number_page}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books_url_parts = soup.find_all('table', class_='d_book')
        for url_part in books_url_parts:
            try:
                book_url = urljoin(
                    url,
                    url_part.find('a')['href']
                )
                book_id = (url_part.find('a')['href']).replace('/', '').replace('b', '')
                book_response = requests.get(book_url)
                check_for_redirect(book_response)
                book_soup = BeautifulSoup(book_response.text, 'lxml')
                title_tag = book_soup.find('h1')
                book_image = book_soup.find('div', class_='bookimage').find('img')['src']
                title_text = title_tag.text
                book_title, book_author = title_text.split('::')
                
                url = 'https://tululu.org/txt.php'
                params = {'id': book_id}
                download_response = requests.get(url, params=params)
                download_response.raise_for_status()
                download_txt(download_response, f'{book_title}.txt'.strip(), 'books')
                book_path = join('books', f'{book_title.strip()}.txt')
                image_path = download_image(urljoin(book_url, book_image))
                # print(image_path)
                # print(book_path)
                genre_field = book_soup.find('span', class_='d_book')
                genres_tags = genre_field.find_all('a')
                genres_texts = [genre_tag.text for genre_tag in genres_tags]

                comments_tags = book_soup.find_all('div', class_='texts')
                comments_texts = [
                    comment_tag.find('span', class_='black').text
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
                print(about_book)
                about_books.append(about_book)
                

            except requests.exceptions.HTTPError:
                continue

    # print(about_books)
    # json_string = json.dumps(about_books, ensure_ascii=False).encode('utf8')
    with open("about_books.json", "w", encoding='utf8') as my_file:
        json.dump(about_books, my_file, ensure_ascii=False)



