import requests
from bs4 import BeautifulSoup as bs
import time
import sys, os


def login(sess, pixiv_id, password, retry, headers):
    base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
    post_key_html = sess.get(base_url, headers=headers, timeout=10).text
    post_key_soup = bs(post_key_html, 'lxml')
    post_key = post_key_soup.find('input', {'name': 'post_key'})['value']
    data = {
        'pixiv_id': pixiv_id,
        'password': password,
        'post_key': post_key
    }

    flag = True
    while flag and retry:
        try:
            sess.post(login_url, data=data, headers=headers)
            print('logged in')
            flag = False
        except Exception:
            retry -= 1
            time.sleep(1)
    if flag:
        print('error occured when log in')
        sys.exit()


def get_illust_id(sess, page_list, headers, retry=3):
    base_url = 'https://www.pixiv.net/bookmark.php?rest=show&type=illust_all&p='

    all_ids = []
    for page in page_list:
        i, flag = 0, True
        while flag and (i < retry):
            try:
                page_url = base_url + str(page)
                html = sess.get(page_url, headers=headers).text
                p1 = html.rfind("pixiv.context.illustRecommendSampleIllust = ")
                p2 = html.find(";pixiv.context.illustRecommendLimit = 500")
                ids_str = html[p1+45:p2-1]
                ids = ids_str.split(',')
                all_ids.extend(ids)
                flag = False
            except Exception:
                i += 1

    return all_ids


def get_image_url(sess, all_ids, headers, retry=3):
    base_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='

    img_urls = []
    for illust_id in all_ids:
        illust_url = base_url + illust_id

        flag = True
        while flag and retry:
            try:
                illust_html = sess.get(illust_url, headers=headers).text
                p1 = illust_html.find('"regular"')
                p2 = illust_html.find('"original"')
                ori_url = illust_html[p1 + 11:p2 - 2]

                img_url = ori_url.replace('\\', "")
                img_urls.append(img_url)
                flag = False
            except Exception:
                retry -= 1
                time.sleep(1)
        if flag:
            print("error in parsing usl %s" % illust_url)

    return img_urls


def download_by_img(sess, img_urls, save_path, headers):
    err_urls = []

    for i, url in enumerate(img_urls):
        name = url.split('/')[-1]
        illust_id = name.split('_')[0]
        refer = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + illust_id
        headers["Referer"] = refer

        try:
            r = sess.get(url, headers=headers, timeout=10, stream=True)
            if r.status_code == requests.codes.ok:
                img_data = r.content
                with open(save_path + name, 'wb') as handler:
                    handler.write(img_data)
                    print('{} have been downloaded'.format(url))
            time.sleep(1)
        except Exception:
            err_urls.append(url)

    return err_urls


def update_bookmark(all_ids, saved_path):
    id_saved = set()
    for img_name in os.listdir(saved_path):
        illust_id = img_name.split('_')[0]
        id_saved.add(illust_id)

    to_be_download = []
    for i in all_ids:
        if i not in id_saved:
            to_be_download.append(i)
    return to_be_download


def main(update=True):
    sess = requests.session()
    headers = {
        'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    }
    login(sess, 'your_pixiv_id', 'your_password', 3, headers)

    headers['Referer'] = 'https://www.pixiv.net/'
    print("Get all illustration_id from bookmarks")
    all_ids = get_illust_id(sess, range(1, 141), headers)

    if update:
        print("filter out illustration that already existed")
        all_ids = update_bookmark(all_ids, "d:\\software\\pixiv_bookmark_download-master\\bookmark\\")
    print("Number of illustrations={} to be download".format(len(all_ids)))

    print("Get image urls from its id")
    img_urls = get_image_url(sess, all_ids, headers)
    print("Number of image urls={}".format(len(img_urls)))

    print("downloading images by urls")
    err_url = download_by_img(sess, img_urls, 'd:\\software\\pixiv_bookmark_download-master\\bookmark\\', headers)
    print(err_url)


if __name__ == "__main__":
    main(update=True)
