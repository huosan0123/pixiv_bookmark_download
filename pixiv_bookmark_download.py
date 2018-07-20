import requests
import json
import time
import os
import shutil
from bs4 import BeautifulSoup

se = requests.session()

headers = {
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.89 Chrome/62.0.3202.89 Safari/537.36'
}


def login(pixiv_id, password):
    base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
    post_key_html = se.get(base_url, headers=headers).text
    post_key_soup = BeautifulSoup(post_key_html, 'lxml')
    post_key = post_key_soup.find('input', {'name': 'post_key'})['value']
    data = {
        'pixiv_id': pixiv_id,
        'password': password,
        'post_key': post_key
    }
    se.post(login_url, data=data, headers=headers)


login('user_fdmt7385', 'lc571924')
headers['Referer'] = 'https://www.pixiv.net/'
html = se.get('https://www.pixiv.net/bookmark.php?rest=show&type=illust_all&p=2', headers=headers)
soup = BeautifulSoup(html.text, 'lxml')
a = soup.find_all('a')
ids = set()
for i in a:
    href = i.get('href')
    if (href) and ('mode=medium&illust_id' in href):
        pos = href.rfind('=') + 1
        ids.add(href[pos:])

print(ids)

base_usrl = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=34352238'

new_html = se.get(base_usrl, headers=headers)
# soup = BeautifulSoup(new_html.text, 'lxml')
# a = soup.find_all('script')
# for i in a:
#     print(type(i))

b = new_html.text
c = b.find("illust: {")
print(b[c:])
