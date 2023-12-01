"""
从对象存储中下载所有文件到本地
"""
from OP import *

if __name__ == '__main__':
    op = OpenPuya()
    # 获取存储桶中所有文件
    response = op.get_all_file()
    for file in response:
        # 下载文件
        op.download(file['Key'])
        print(f'Download {file["Key"]}')

