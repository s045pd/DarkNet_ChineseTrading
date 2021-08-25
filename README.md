![mosaic.jpg](media/mosaic.jpg)
## DarkNet_ChineseTrading - 暗网中文网监控实时爬虫
![](https://img.shields.io/badge/language-python3-orange.svg)
![](https://img.shields.io/badge/platform-mac|lunix|window-orange.svg)

> [En_Doc](https://github.com/aoii103/DarkNet_ChineseTrading/blob/master/README_en.md)
> [教程:如何实现暗网交易监控](https://mp.weixin.qq.com/s/OaPjAaNcEefQxaXQykheqg)

## 监控大屏(grafana快速实现)
![](media/grafana.png)

## 功能

- Tor节点切换
- 自动注册(中文式账户)
- 自动登录
- 防封禁
- ORM交互
- 事件详情/样本信息录入
- 事件提醒（`telegram`）[图文]
- 分类爬取
- 裸体图片过滤(保存但不发送)
- 残留EXIF-GPS信息提取
- 新增 [ddddocr](https://github.com/sml2h3/ddddocr) 验证码识别

加入我们：[https://t.me/fordarknetspiderbot](https://t.me/fordarknetspiderbot)

## 使用

准备好 `docker` 或 `podman` 及 `docker-compose`

```bash
git clone https://github.com/s045pd/DarkNet_ChineseTrading.git
cd DarkNet_ChineseTrading
docker-compose build --pull && docker-compose --env-file .env.default up
```

## TODO

- 宿主机Socks5代理
- Grafana界面
