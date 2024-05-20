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
--data 'url=http://app:5000/restaurant_api'

curl -i -X POST \
  --url http://kong:8001/services/restaurant_api/routes \
  --data 'paths[]=/restaurant_api' \
  --data 'service.name=restaurant_api'

curl -i -X POST \
  --url http://kong:8001/consumers/ \
  --data "username=postman_client"

curl -i -X POST \
  --url http://kong:8001/consumers/postman_client/jwt \
  --data "algorithm=RS256" \
  --data "key=my_key" \
  --data "rsa_public_key=/keys/public_key.pem"

curl -i -X POST \
  --url http://kong:8001/services/restaurant_api/plugins \
  --data "name=jwt" \
  --data "config.claims_to_verify=exp" \
  --data "config.secret_is_base64=false" \
  --data "config.key_claim_name=iss" \
  --data "config.uri_param_names=jwt" \
  --data "config.anonymous=false"

#  curl -i -X POST \
#  --url http://localhost:8001/services/order_api/plugins \
#  --data "name=jwt"
#
#  curl -i -X POST \
#  --url http://localhost:8001/services/delivery_api/plugins \
#  --data "name=jwt"

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
