#!/bin/bash

# First argument is the check type
CHECK_TYPE=$1

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERS_DIR="${SCRIPTS_DIR}/../users/"


# Iterate over each JSON file in the users directory
for user_file in $USERS_DIR*.json; do
    DOMAINS=$(jq -r '.domains[].name' "$user_file")
    
    for domain in $DOMAINS; do
      case $CHECK_TYPE in
        --all)
          echo "$domain"
          bash ${SCRIPTS_DIR}/http_response_check.sh $domain
          bash ${SCRIPTS_DIR}/ssl_check.sh $domain
          bash ${SCRIPTS_DIR}/whois_check.sh $domain
          echo "____________________________________________________________"
          ;;
        http_response_check)
          bash ${SCRIPTS_DIR}/http_response_check.sh $domain
          ;;
        ssl_check)
          bash ${SCRIPTS_DIR}/ssl_check.sh $domain
          ;;
        whois_check)
          bash ${SCRIPTS_DIR}/whois_check.sh $domain
          ;;

        *)
          echo "Invalid check type specified"
          exit 1
          ;;
      esac
    done
done

