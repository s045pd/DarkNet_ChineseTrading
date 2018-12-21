kill -9 `lsof -i:9150|grep LISTEN|grep -v grep|awk '{print $2}'`
tor
