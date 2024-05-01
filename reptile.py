"""
此文件用来从普冉官网拉取所有的文件到本地
"""
import os

import requests
from OP import OpenPuya
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm

base_url = 'https://www.puyasemi.com/download.html'  # 所有文件的下载地址

logging.basicConfig(level=logging.INFO)


def download_file(url: str, path: str):
    """
    下载文件，显示文件名下载速度，预估时间，下载的大小
    :param url: 下载地址
    :param path: 保存地址
    :return:
    """
    # 如果文件夹不存在则创建
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # 如果文件已经存在就不下载
    if os.path.exists(path):
        return

    # 检测链接是否有效，如果404就不下载
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        return

    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    filename = url.split("/")[-1]

    with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=filename) as progress_bar:
        with open(path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")

def download_item(file,series):
    try:
        download_cn_url = 'https://www.puyasemi.com'
        download_cn_url += file.find('div').find_all('div', class_='y1 f16')[2].find('a').get('href')
        file_name = download_cn_url.split('/')[-1]
        download_file(download_cn_url, os.path.join(OpenPuya.base_path, series, 'zh-CN', file_name))
    except AttributeError:
        download_cn_url = ''

    try:
        download_en_url = 'https://www.puyasemi.com'
        download_en_url += file.find('div').find_all('div', class_='y1')[2].find('a').get('href')
        file_name = download_en_url.split('/')[-1]
        download_file(download_en_url, os.path.join(OpenPuya.base_path, series, 'en', file_name))

    except AttributeError:
        download_en_url = ''

def main():
    # 获取html文件
    response = requests.get(base_url)
    # 用BeautifulSoup解析html文件
    soup = BeautifulSoup(response.text, 'html.parser')
    # 遍历body下的所有section标签，其中class为download p100 p100_的数据
    for section in soup.body.find_all('section', class_='download p100 p100_'):
        # 遍历section下的class为load_3 wow slideInUp的div标签
        for i in section.find_all('div', class_='load_3 wow slideInUp'):
            # 遍历这个div下的class为slide的div标签
            for j in i.find_all('div', class_='slide'):
                # pu_table2的逻辑

                # 如果two的div下存在class为three active的div标签
                temp = j.find('div', class_='two').find_all('div', class_='three')
                if j.find('div', class_='two').find('div', class_='three'):
                    for k in j.find('div', class_='two').find_all('div', class_='three'):
                        try:
                            series = k.find('div', class_='th_1 df').find('div', class_='flex df ac').find('div', class_='ex df ac').find('p', class_='f20').text
                        except AttributeError:
                            continue

                        logging.info(f'开始下载{series}的文件')
                        files = k.find('div', class_='th_2').find('div', class_='tbody').find_all('div', class_='item')
                        for file in files:
                            download_item(file,series)

                # 如果是pu_table1
                # 获取这个div下的class为one df的div的class为txt df ac的class为f20的p标签的文本
                try:
                    series = j.find('div', class_='one df') \
                        .find('div', class_='flex df ac') \
                        .find('div', class_='txt df ac') \
                        .find('p', class_='f20') \
                        .text
                except AttributeError:
                    continue

                logging.info(f'开始下载{series}的文件')
                files = j.find('div', class_='two').find('div', class_='tbody').find_all('div', class_='item')
                for file in files:
                    download_item(file,series)



if __name__ == '__main__':
    main()
