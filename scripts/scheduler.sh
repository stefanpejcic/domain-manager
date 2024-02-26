#!/bin/bash

# First argument is the check type
CHECK_TYPE=$1

# Define path to your MySQL configuration file
DB_CONF="/root/domain-manager-main/db.cnf"

# Define the database name
DB_NAME="domains"

# Fetch domains
DOMAINS=$(mysql --defaults-extra-file=$DB_CONF $DB_NAME -e "SELECT domain FROM domains;" -s --skip-column-names)

# Perform the specified check for each domain
for domain in $DOMAINS; do
  case $CHECK_TYPE in
    http_response_check)
      bash /root/domain-manager-main/scripts/http_response_check.sh $domain
      ;;
    ssl_check)
      bash /root/domain-manager-main/scripts/ssl_check.sh $domain
      ;;
    whois_check)
      bash /root/domain-manager-main/scripts/whois_check.sh $domain
      ;;
    *)
      echo "Invalid check type specified"
      exit 1
      ;;
  esac
done
