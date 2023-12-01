from OP import *
import os
import fnmatch

include_path = [
    "datasheet", # 数据手册列表
]

def get_ignore() -> list:
    with open('.gitignore') as f:
        return f.readlines()

if __name__ == '__main__':
    op = OpenPuya()
    for path in include_path:
        path = os.path.join(op.base_path,path)
        for file in os.listdir(path):
            # 判断是否在忽略列表中，支持通配符
            if any(fnmatch.fnmatch(file,ignore) for ignore in get_ignore()):
                continue
            op.upload(os.path.join(path,file))