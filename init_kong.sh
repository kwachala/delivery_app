#!/bin/sh

# Install curl
apk --no-cache add curl

## Wait for PostgreSQL to be ready
#while ! pg_isready -h kong-db -p 5432 -U kong; do
#  echo 'Waiting for PostgreSQL to be ready...';
#  sleep 5;
#done;

# Wait for Kong to be ready
while ! curl -s -o /dev/null http://kong:8000; do
  echo 'Waiting for Kong to be ready...';
  sleep 5;
done;

echo 'Kong is up and running. Executing configuration script...';

curl -i -X POST \
--url http://kong:8001/services/ \
--data 'name=restaurant_api' \
--data 'url=http://restaurant-app:5000/restaurant_api'

curl -i -X POST \
  --url http://kong:8001/services/restaurant_api/routes \
  --data 'paths[]=/restaurant_api' \

curl -i -X POST \
--url http://kong:8001/services/ \
--data 'name=deliveries_api' \
--data 'url=http://deliveries-app:5001/deliveries_api'

curl -i -X POST \
  --url http://kong:8001/services/deliveries_api/routes \
  --data 'paths[]=/deliveries_api' \

echo
echo 'Configuration completed.';

## Configure Kong services, routes, plugins, and consumers
#curl -i -X POST http://kong:8000/services/ \
#  --data "name=restaurant-service" \
#  --data "url=http://app:5000";
#
#curl -i -X POST http://kong:8000/services/restaurant-service/routes \
#  --data "paths[]=/restaurant_api/restaurant";
#
#curl -i -X POST http://kong:8000/services/restaurant-service/plugins \
#  --data "name=key-auth";
#
#curl -i -X POST http://kong:8000/consumers/ \
#  --data "username=admin";
#
#curl -i -X POST http://kong:8000/consumers/admin/key-auth/ \
#  --data "key=admin-key";
#
#echo 'Configuration script completed.';
