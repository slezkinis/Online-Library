import requests
import os
from pathlib import Path


if __name__ == '__main__':
    directry = 'books'
    Path(directry).mkdir(parents=True, exist_ok=True)
    for book_id in range(1, 11):
        filename = f'book_{book_id}.txt'
        url = 'https://tululu.org/txt.php'
        params = {'id': book_id}
        response = requests.get(url, params=params)
        response.raise_for_status()
        with open(os.path.join(directry, filename), 'wb') as file:
            file.write(response.content)