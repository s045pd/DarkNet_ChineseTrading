kill -9 `lsof -i:9150|grep LISTEN|awk '{print $2}'`
tor
