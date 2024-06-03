#!/bin/sh

# Install curl
#apk --no-cache add curl
apk update && apk add --no-cache curl

#docker-compose up -d kong-db kong kong-migration

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
--data 'name=user_api' \
--data 'url=http://user-app:5001/user_api'

curl -i -X POST \
  --url http://kong:8001/services/user_api/routes \
  --data 'paths[]=/user_api' \

curl -i -X POST http://kong:8001/consumers \
  --data "username=consumer-user"

curl -i -X POST http://kong:8001/consumers/consumer-user/jwt \
  --data "key=$JWT_KEY" \
  --data "secret=$JWT_SECRET"

# Poświadczenia JWT dla konsumenta
RESPONSE=$(curl -s -X POST http://kong:8001/consumers/consumer-user/jwt)

echo "JWT plugin response: $RESPONSE"

curl -i -X POST \
  --url http://kong:8001/services/restaurant_api/plugins \
  --data "name=jwt" \
  --data "config.claims_to_verify=exp" \
  --data "config.secret_is_base64=false" \
  --data "config.key_claim_name=iss" \
  --data "config.uri_param_names=jwt" \
  --data "config.anonymous=false"

echo 'Configuration completed.';