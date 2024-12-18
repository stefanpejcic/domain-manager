#!/bin/bash

# First argument is the check type
CHECK_TYPE=$1

USERS_DIR="users/"

# Iterate over each JSON file in the users directory
for user_file in $USERS_DIR*.json; do
    DOMAINS=$(jq -r '.domains[].name' "$user_file")
    
    for domain in $DOMAINS; do
      case $CHECK_TYPE in
        --all)
          echo "$domain"
          bash /root/domain-manager/scripts/http_response_check.sh $domain
          bash /root/domain-manager/scripts/ssl_check.sh $domain
          bash /root/domain-manager/scripts/whois_check.sh $domain
          echo "____________________________________________________________"
          ;;
        http_response_check)
          bash /root/domain-manager/scripts/http_response_check.sh $domain
          ;;
        ssl_check)
          bash /root/domain-manager/scripts/ssl_check.sh $domain
          ;;
        whois_check)
          bash /root/domain-manager/scripts/whois_check.sh $domain
          ;;

        *)
          echo "Invalid check type specified"
          exit 1
          ;;
      esac
    done
done

