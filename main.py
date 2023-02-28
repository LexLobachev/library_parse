import requests
import os

directory = 'books'

if not os.path.exists(directory):
    os.makedirs(directory)

url = "https://tululu.org/txt.php"
params = {
    'id': 1
}
for book_id in range(1, 11):
    response = requests.get(url=url, params=params)
    response.raise_for_status()

    filename = f'id{book_id}.txt'
    with open(os.path.join(directory, filename), 'wb') as file:
        file.write(response.content)
    params['id'] += 1
