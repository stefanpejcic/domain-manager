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



check_domain() {
    local domain=$1
    local check_script=$2
    local timeout=$3
    if ! timeout "$timeout" bash "$check_script" "$domain"; then
        echo "$check_script failed for $domain after $timeout seconds"
    fi
}

for user_file in $USERS_DIR*.json; do
    DOMAINS=$(jq -r '.domains[].name' "$user_file")
    
    for domain in $DOMAINS; do
        echo "$domain"
        case $CHECK_TYPE in
            --all)
                check_domain "$domain" "${SCRIPTS_DIR}/http_response_check.sh" 15
                check_domain "$domain" "${SCRIPTS_DIR}/ssl_check.sh" 5
                check_domain "$domain" "${SCRIPTS_DIR}/whois_check.sh" 10
                ;;
            http_response_check)
                check_domain "$domain" "${SCRIPTS_DIR}/http_response_check.sh" 15
                ;;
            ssl_check)
                check_domain "$domain" "${SCRIPTS_DIR}/ssl_check.sh" 5
                ;;
            whois_check)
                check_domain "$domain" "${SCRIPTS_DIR}/whois_check.sh" 10
                ;;
            *)
                usage
                ;;
        esac
        echo "____________________________________________________________"
    done
done

