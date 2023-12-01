# OpenPuya data

OpenPuya资源文件托管交互的仓库。目前采用cloudflare R2作为对象存储，贡献者请联系管理员获取相关API权限。

## 使用方法

请在根目录下新建一个 `__config.json`，其中存放访问的相关API授权信息，一个典型的模板如下：

```json
{
  "Cloudflare-Token": "",
  "S3-ID": "",
  "S3-Key": "",
  "S3-Url": ""
}
```

具体的授权信息请联系管理员获取。
