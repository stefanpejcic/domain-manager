#!/bin/bash

CHECK_TYPE=$1
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERS_DIR="${SCRIPTS_DIR}/../users/"


usage() {
    echo "Usage: $0 [--all|http_response_check|ssl_check|whois_check]"
    echo
    echo "Options:"
    echo "  --all                 Run all checks (http_response_check, ssl_check, whois_check) for all domains."
    echo "  http_response_check   Run HTTP response check for each domain."
    echo "  ssl_check             Run SSL certificate check for each domain."
    echo "  whois_check           Run WHOIS lookup for each domain."
    echo
    echo "This script processes user files and performs checks based on the provided option."
}


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
          usage
          exit 1
          ;;
      esac
    done
done

