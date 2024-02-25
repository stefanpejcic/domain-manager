#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <domain>"
  exit 1
fi

domain=$1
output_file="ssl_info/$domain"

# Ensure the 'ssl_info' directory exists
mkdir -p ssl_info

timestamp=$(date +"%Y-%m-%d %H:%M:%S")

ssl_info=$(openssl s_client -servername "$domain" -connect "$domain":443 -showcerts </dev/null 2>/dev/null | openssl x509 -noout -dates -issuer -subject)

if [ -z "$ssl_info" ]; then
  echo "Failed to retrieve SSL information for $domain"
  echo -e "Timestamp: $timestamp - Error: Failed to retrieve SSL information" >> "$output_file"
  exit 1
fi

expiration_date=$(echo "$ssl_info" | awk -F= '/notAfter/ {print $2}')
issuer=$(echo "$ssl_info" | awk -F= '/issuer/ {print $2}')
subject=$(echo "$ssl_info" | awk -F= '/subject/ {print $2}')

echo -e "Timestamp: $timestamp - Issuer: $issuer - Subject: $subject - Expiration Date: $expiration_date" >> "$output_file"

echo "SSL info: $output_file"
