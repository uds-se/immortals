cat $1 | sed -e 's/#.*//g' -e 's#(.*##g' | awk '/def *test/{print$2}'
