#!/bin/sh

# This script runs inside the docker container. 
# It configures nginx from the shell environment, and starts nginx.
# We need to know about the back end since we're proxying it to simplify CORS. 
if [ -z "$BE_SERVICE_NAME" ]; then
  echo "Error: BE_SERVICE_NAME is not set"
  exit 1
fi
if [ -z "$BE_SERVICE_PORT" ]; then
  echo "Error: SERVER_PORT is not set"
  exit 1
fi
envsubst '$BE_SERVICE_NAME $BE_SERVICE_PORT' < /nginx.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'