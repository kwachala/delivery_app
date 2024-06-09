#!/bin/sh

apk update && apk add curl || exit 1

while ! curl -s -o /dev/null http://kong:8000; do
  echo 'Waiting for Kong to be ready...'
  sleep 5
done

echo 'Kong is up and running. Executing configuration script...'

curl -i -X POST \
--url http://kong:8001/services/ \
--data 'name=restaurant_api' \
--data 'url=http://app:5000/restaurant_api'

curl -i -X POST \
  --url http://kong:8001/services/restaurant_api/routes \
  --data 'paths[]=/restaurant_api'

curl -i -X POST \
--url http://kong:8001/services/ \
--data 'name=order_api' \
--data 'url=http://app:5001/order_api'

curl -i -X POST \
  --url http://kong:8001/services/order_api/routes \
  --data 'paths[]=/order_api' \

echo
echo 'Configuration completed.'