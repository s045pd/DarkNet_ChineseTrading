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

注意事项：

- 需要全局F墙环境，测试可在 [https://ide.goorm.io/](https://ide.goorm.io/) 部署
- 未改TG判断，需再 [.env.default](.env.default)下配置好TG
- 准备好 `docker` 或 `podman` 及 `docker-compose`
- 首次启动似乎会报无法解析到 `db`，再起一次就好了

```bash
git clone https://github.com/s045pd/DarkNet_ChineseTrading.git
cd DarkNet_ChineseTrading
docker-compose build --pull && docker-compose --env-file .env.default up
```

<img width="1427" alt="Pasted Graphic 1" src="https://user-images.githubusercontent.com/22721729/130713991-17897b03-ddea-4c53-aff7-976fc13fc90e.png">


## TODO

- 宿主机Socks5代理
- Grafana界面
