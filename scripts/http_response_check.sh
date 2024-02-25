#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <domain>"
  exit 1
fi

domain=$1
output_file="responses/$domain"

# Ensure the 'responses' directory exists
mkdir -p responses

timestamp=$(date +"%Y-%m-%d %H:%M:%S")

http_response=$(curl --write-out '%{http_code}' --silent --output /dev/null $domain)

if [[ $http_response =~ ^3 ]]; then
  http_response=$(curl -LIsS "https://$domain" | head -n 1 | awk '{print $2}')
fi

echo "$timestamp - $http_response" >> "$output_file"

echo "HTTP response saved to: $output_file"
