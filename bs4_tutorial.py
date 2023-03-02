import requests
from bs4 import BeautifulSoup


url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()
# print(response.text)

soup = BeautifulSoup(response.text, 'lxml')
# print(soup.prettify())
# print(soup.find('h1'))
title_tag = soup.find('main').find('header').find('h1')
title_text = title_tag.text
print(title_text)

post_img = soup.find('img', class_='attachment-post-image')['src']
print(post_img)

post_tag = soup.find('div', class_='entry-content').find('p')
post_text = post_tag.text
print(post_text)
