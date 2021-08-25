![mosaic.jpg](media/mosaic.jpg)

## DarkNet_ChineseTrading - A crawler for real-time monitoring of the dark network website.

![](https://img.shields.io/badge/language-python3-orange.svg)
![](https://img.shields.io/badge/platform-mac|lunix|window-orange.svg)

> [Tutorial: How to Implement Dark Net Transaction Monitoring] (https://mp.weixin.qq.com/s/OaPjAaNcEefQxaXQykheqg)

## Monitor screen(by grafana)

![](media/grafana.png)

## Features

- Automatic Tor node switch
- Automatic registration
- Automatic Log-in
- Anti-ban
- ORM
- Event details
- Event reminder（telegram）[Graphic with Photo]
- Nude Image Filter
- EXIF GPS Detect
- New Capcha Solution [ddddocr](https://github.com/sml2h3/ddddocr)

join us：[https://t.me/fordarknetspiderbot](https://t.me/fordarknetspiderbot)

## Use

- you can test it on [https://ide.goorm.io/](https://ide.goorm.io/)
- telegram configure is necessary at [.env.default](.env.default)
- prepare `docker` or `podman` and `docker-compose`


```bash
git clone https://github.com/s045pd/DarkNet_ChineseTrading.git
cd DarkNet_ChineseTrading
docker-compose build --pull && docker-compose --env-file .env.default up
```

## TODO

- Host Socks5 Proxy
- Grafana Page
