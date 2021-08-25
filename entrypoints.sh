#/bin/sh

set -e
cd /opt

echo 'SOCKSPort 9050' >torrc
if [ ! -z $TOR_FORWORD_SOCKS5_PROXY ]; then
    echo "Socks5Proxy $TOR_FORWORD_SOCKS5_PROXY" >>torrc
fi
echo 'RunAsDaemon 1
ControlPort 9051' >>torrc

tor -f torrc
cd /opt/darknet
python3 -m darknet

sleep infinity
