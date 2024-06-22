from OP import OpenPuya, zh_en_map
import os
import fnmatch
import time
import json
import logging

base_url = "https://download.py32.org/"

include_path = [
    "Application Note",
    "Datasheet&Reference manual",
    "PACK_IAR",
    "PACK_MDK",
    "Tool",
    "工具",
    "应用方案",
    "应用笔记",
    "数据手册",
    "用户手册"
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

    def ignore_file(file: str) -> bool:
        for ignore in get_ignore():
            if fnmatch.fnmatch(file, ignore):
                return True
        return False

    for path in user_path:
        all_file[path] = []
        file_path = os.path.join(OpenPuya.base_path, path)
        for file in os.listdir(file_path):
            # 判断是否在忽略列表中，支持通配符
            if ignore_file(file):
                continue

            if os.path.isfile(os.path.join(file_path, file)):
                all_file[path].append(file)
                continue

            for root, dirs, files in os.walk(os.path.join(file_path, file)):
                for f in files:
                    if ignore_file(f):
                        continue
                    all_file[path].append(os.path.join(root, f).replace(file_path + "\\", ""))

    return all_file


def push(op: OpenPuya):
    all_file = get_all_file()
    upstream_file = op.get_all_file()
    # 处理一下upstream_file中的元素，只保留文件名
    upstream_file = [file.split('/')[-1] for file in upstream_file]
    for path in all_file:
        for file in all_file[path]:
            # 判断是否需要上传
            if file.replace('\\', '/').split('/')[-1] in upstream_file:
                continue

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
            # 如果没有config.json则跳过
            if not os.path.exists(os.path.join(markdown_path, dir, "config.json")):
                continue
            # 读取config.json
            with open(os.path.join(markdown_path, dir, "config.json"), encoding="utf-8") as f:
                config = json.load(f)
            for language in config:
                file_name = os.path.join(markdown_path, dir, language + ".md")
                with open(file_name, "w", encoding="utf-8") as f:
                    for group in config[language]:
                        f.write("## " + group + "\n")
                        match language:
                            case "zh-CN":
                                f.write("| 文件名 | 更新时间 | 大小 | 下载地址 |\n")
                            case "en":
                                f.write("| File name | Update time | Size | Download address |\n")

                        f.write("| :----: | :----: | :----: | :----: |\n")

                        # 如果config内容非空并且第一个元素是en则使用en语言
                        if config[language][group] != [] and config[language][group][0] == 'en':
                            language = 'en'
                            group = zh_en_map[group]

                        for file in config[language][group]:
                            # 取最后一个'/'后面的字符串作为文件名，如果没有'/'则取全部字符串
                            if '/' in file:
                                name = file.split('/')[-1]
                            else:
                                name = file

                            file = language + '/' + file  # 实际的路径中间还有语言

                            match language:
                                case "zh-CN":
                                    real_group = group
                                case "en":
                                    # 根据zh_en_map中的值的英文名称取其键
                                    if group in zh_en_map.values():
                                        real_group = list(zh_en_map.keys())[list(zh_en_map.values()).index(group)]
                                    else:
                                        real_group = group
                                case _:
                                    real_group = group

                            update_time = time2human(
                                os.path.getmtime(os.path.join(OpenPuya.base_path, real_group, file)))
                            size = bytes2human(os.path.getsize(os.path.join(OpenPuya.base_path, real_group, file)))
                            # real_group 如果是在zh_en_map中则替换为英文名称

                            match language:
                                case "zh-CN":
                                    if group in zh_en_map:
                                        real_group = zh_en_map[group]
                                    else:
                                        real_group = group
                                case "en":
                                    real_group = group
                                case _:
                                    real_group = group

                            url = base_url + url_encode(real_group) + "/" + url_encode(file)
                            f.write(
                                f"| {name} | {update_time} | {size} | <{url}> |\n"
                            )
                logging.info("生成markdown文件：" + file_name)


if __name__ == '__main__':
    op = OpenPuya()
    # 上传本地的文件到对象存储
    push(op)
    # 生成markdown
    markdown()
