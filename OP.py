import json
import boto3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 中文名称和英文名称的map
zh_en_map = {
    "数据手册": "Datasheet",
    "用户手册": "ReferenceManual",
    "应用笔记": "ApplicationNote",
    "应用方案": "ApplicationSolution",
    "工具": "Tool",
}


class OpenPuya:
    _config_path = './__config.json'
    _bucket_name = 'openpuya'
    base_path = './file'

    def get_config(self) -> dict:
        with open(self._config_path) as f:
            return json.load(f)

    def __init__(self):
        self.config = self.get_config()
        self.s3 = boto3.client('s3', endpoint_url=self.config['S3-Url'], aws_secret_access_key=self.config['S3-Key'],
                               aws_access_key_id=self.config['S3-ID'])

    def upload(self, local_path: str):
        remote_path = local_path.replace('\\', '/').replace('./', '')
        # 去掉远程路径的base_path前缀
        remote_path = remote_path.replace(
            (self.base_path + '/').replace('\\', '/').replace('./', ''),
            ''
        )
        # 将remote_path按照'/'进行分割，如果第一个路径中有zh_en_map中的中文名称则替换为英文名称
        remote_path = remote_path.split('/')
        if remote_path[0] in zh_en_map:
            remote_path[0] = zh_en_map[remote_path[0]]
        remote_path = '/'.join(remote_path)
        

        logging.info(f'upload {local_path} to {remote_path}')
        self.s3.upload_file(local_path, self._bucket_name, remote_path)

    def download(self, remote_path: str):
        real_remote_path = remote_path
        # 将remote_path按照'/'进行分割，如果第一个路径中有zh_en_map中的英文名称则替换为中文名称
        remote_path = remote_path.split('/')
        if remote_path[0] in zh_en_map.values():
            remote_path[0] = list(zh_en_map.keys())[list(zh_en_map.values()).index(remote_path[0])]
        remote_path = '/'.join(remote_path)
        
        local_path = os.path.join(self.base_path, remote_path)

        logging.info(f'download {remote_path} to {local_path}')
        # 如果文件夹不存在则创建
        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))
        try:
            self.s3.download_file(self._bucket_name, real_remote_path, local_path)
        except Exception as e:
            logging.error(f'error: {e}')

    def get_all_file(self):
        response = self.s3.list_objects_v2(Bucket=self._bucket_name)
        response = response['Contents']

        file = []
        for obj in response:
            file.append(obj['Key'])
        try:
            return file
        except KeyError:
            print('Bucket is empty')
            return []
