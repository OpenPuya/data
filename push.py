from OP import *
import os
import fnmatch
import time

include_path = [
    "Datasheet&Reference manual", # 数据手册列表

]

markdown_dict = [
    {
        "name": "PY32F030",
        "path": ["Datasheet&Reference manual"]
    }
]

url = "https://download.py32.org/"

def get_ignore() -> list:
    with open('.gitignore') as f:
        return f.readlines()

def markdown_file(f:str) -> bool:
    """
    判断markdown_dict中的文件是否需要生成markdown，去掉忽略列表中的文件，已经仅匹配markdown_dict中包含name的文件
    :param f:
    :return:
    """
    gitignore = get_ignore()
    for ignore in gitignore:
        if fnmatch.fnmatch(f, ignore):
            return False
    for series in markdown_dict:
        if series['name'] in f:
            return True
    return False

def get_all_file() -> dict:
    all_file = {}
    for path in include_path:
        all_file[path] = []
        file_path = os.path.join(OpenPuya.base_path, path)
        for file in os.listdir(file_path):
            # 判断是否在忽略列表中，支持通配符
            if any(fnmatch.fnmatch(file, ignore) for ignore in get_ignore()):
                continue
            all_file[path].append(file)
    return all_file
def push(op:OpenPuya):
    all_file = get_all_file()
    for path in all_file:
        for file in all_file[path]:
            upload_path = os.path.join(op.base_path, path, file)
            op.upload(upload_path)

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 K'
    >>> bytes2human(100001221)
    '95.4 M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f %s' % (value, s)
    return '%.1f B' % (n)

def time2human(n):
    """
    将时间戳转换为人类可读的时间
    :param n:
    :return:
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(n))

def url_encode(url:str) -> str:
    """
    将url中的特殊字符转换为url编码
    :param url:
    :return:
    """
    import urllib.parse
    return urllib.parse.quote(url)
def markdown():
    all_file = get_all_file()
    for series in markdown_dict:
        md_str = ""
        series_name = series['name']
        series_path = series['path']
        for path in series_path:
            file = all_file[path]
            md_str += f"## {path}\n"
            md_str += f"|文件名|更新时间|大小|下载地址|\n"
            md_str += f"|---|---|---|---|\n"
            for f in file:
                if not markdown_file(f):
                    continue
                file_name = f
                file_path = url + url_encode(path + '/' + f)
                file_size = bytes2human(os.path.getsize(os.path.join(OpenPuya.base_path, path, f)))
                file_time = time2human(os.path.getmtime(os.path.join(OpenPuya.base_path, path, f)))
                md_str += f"|{file_name}|{file_time}|{file_size}|<{file_path}>|\n"
        markdown_path = os.path.join("markdown", series_name + ".md")
        if not os.path.exists("markdown"):
            os.mkdir("markdown")
        with open(markdown_path, 'w',encoding="utf-8") as f:
            f.write(md_str)


if __name__ == '__main__':
    op = OpenPuya()
    # 上传本地的文件到对象存储
    push(op)
    # 生成markdown
    markdown()

