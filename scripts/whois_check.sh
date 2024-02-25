#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <domain>"
  exit 1
fi

domain=$1
output_file="whois_results/$domain.txt"

# Ensure the 'whois_results' directory exists
mkdir -p whois_results

timestamp=$(date +"%Y-%m-%d %H:%M:%S")

# Check if 'whois' command is available
if ! command -v whois &> /dev/null; then
  echo "'whois' command not found. Installing it..."
  sudo apt-get update
  sudo apt-get install -y whois
fi

# Check again if 'whois' is now available
if command -v whois &> /dev/null; then
  whois_result=$(whois "$domain")

  # Extract relevant information using awk
  registration_date=$(echo "$whois_result" | awk '/Creation Date:/ {print substr($0, index($0,$3))}')
  registrar=$(echo "$whois_result" | awk '/Registrar:/ {print substr($0, index($0,$2))}')
  expiration_date=$(echo "$whois_result" | awk '/Registry Expiry Date:/ {print substr($0, index($0,$4))}')
  status=$(echo "$whois_result" | awk '/Domain status:/ {print substr($0, index($0,$3))}')
  dnssec=$(echo "$whois_result" | awk '/DNSSEC signed:/ {print substr($0, index($0,$4))}')
  
  # Extract nameservers, taking care to handle multiple lines
  nameservers=$(echo "$whois_result" | awk '/DNS:/ {getline; print substr($0, index($0,$1))}')

  # Save the extracted information to the output file
  echo -e "$timestamp - Registration Date: $registration_date - Registrar: $registrar - Expiration Date: $expiration_date - Status: $status - DNSSEC: $dnssec - Name Servers: $nameservers" >> "$output_file"
  
  echo "WHOIS information saved to: $output_file"
else
  echo "Failed to install 'whois'. Please install it manually and rerun the script."
fi
