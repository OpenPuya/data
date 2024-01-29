from OP import *
import os
import fnmatch
import time

base_url = "https://download.py32.org/"

include_path = [
    "Application Note",
    "Datasheet&Reference manual",
    "PACK_IAR",
    "PACK_MDK",
]


def get_ignore() -> list:
    with open('.gitignore') as f:
        return f.readlines()


def markdown_file(f: str, series: dict, i18n: str = "en-US") -> bool:
    """
    判断markdown_dict中的文件是否需要生成markdown，去掉忽略列表中的文件，已经仅匹配markdown_dict中包含name的文件
    :param f:
    :return:
    """
    gitignore = get_ignore()
    for ignore in gitignore:
        if fnmatch.fnmatch(f, ignore):
            return False

    for rule in i18n_rules:
        if rule['i18n'] == i18n:
            for suffix in rule['suffix']:
                # 去掉name末尾的x后缀，只去后缀
                name = series['name'].replace('x', '', -1)
                if name in f:
                    # 只要是文件名中包含了i18n的字符串就返回True
                    if suffix in f or i18n == 'zh-CN':
                        return True
    return False


def get_all_file(user_path: list = include_path) -> dict:
    all_file = {}
    for path in user_path:
        all_file[path] = []
        file_path = os.path.join(OpenPuya.base_path, path)
        for file in os.listdir(file_path):
            # 判断是否在忽略列表中，支持通配符
            if any(fnmatch.fnmatch(file, ignore) for ignore in get_ignore()):
                continue
            if os.path.isfile(os.path.join(file_path, file)):
                all_file[path].append(file)
            else:
                for root, dirs, files in os.walk(os.path.join(file_path, file)):
                    for f in files:
                        if any(fnmatch.fnmatch(file, ignore) for ignore in get_ignore()):
                            continue
                        all_file[path].append(os.path.join(root, f).replace(file_path + "\\", ""))

    return all_file


def push(op: OpenPuya):
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
        prefix[s] = 1 << (i + 1) * 10
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


def url_encode(url: str) -> str:
    """
    将url中的特殊字符转换为url编码
    :param url:
    :return:
    """
    import urllib.parse
    return urllib.parse.quote(url)


def markdown():
    all_file = get_all_file()
    # 递归遍历markdown目录下的所有文件
    markdown_path = os.path.join("./", 'markdown')
    for dir in os.listdir(markdown_path):
        if os.path.isdir(os.path.join(markdown_path, dir)):
            # 读取config.json
            with open(os.path.join(markdown_path, dir, "config.json"), encoding="utf-8") as f:
                config = json.load(f)
            for language in config:
                file_name = os.path.join(markdown_path, dir, language + ".md")
                with open(file_name, "w", encoding="utf-8") as f:
                    for group in config[language]:
                        f.write("## " + group + "\n")
                        match language:
                            case "zh_CN":
                                f.write("| 文件名 | 更新时间 | 大小 | 下载地址 |\n")
                            case "en":
                                f.write("| File name | Update time | Size | Download address |\n")

                        f.write("| :----: | :----: | :----: | :----: |\n")
                        for file in config[language][group]:
                            name = file
                            update_time = time2human(os.path.getmtime(os.path.join(OpenPuya.base_path, group, file)))
                            size = bytes2human(os.path.getsize(os.path.join(OpenPuya.base_path, group, file)))
                            url = base_url + url_encode(group) + "/" + url_encode(file)
                            f.write(
                                "| " + name + " | " + update_time + " | " + size + " | " + url + " |\n"
                            )
                logging.info("生成markdown文件：" + file_name)


if __name__ == '__main__':
    op = OpenPuya()
    # 上传本地的文件到对象存储
    push(op)
    # 生成markdown
    markdown()
