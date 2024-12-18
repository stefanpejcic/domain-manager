#!/bin/bash

CHECK_TYPE=$1
USERNAME=$2 
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERS_DIR="${SCRIPTS_DIR}/../users/"

# valid check types
ALL="--all"
HTTP="http_response_check"
SSL="ssl_check"
WHOIS="whois_check"

usage() {
    echo "Usage: $0 [$ALL|$HTTP|$SSL|$WHOIS] [username]"
    echo
    echo "Options:"
    echo "  $ALL                 Run all checks (http_response_check, ssl_check, whois_check) for all domains."
    echo "  $HTTP   Run HTTP response check for each domain."
    echo "  $SSL             Run SSL certificate check for each domain."
    echo "  $WHOIS           Run WHOIS lookup for each domain."
    echo "  username              (Optional) Specify a username to check only that user's domains."
    echo
    echo "This script processes user files and performs checks based on the provided option."
}

help() {
    echo "This script processes user files and performs SSL, WHOIS or HTTP response checks for user domains."
    echo ""
    usage
}

check_domain() {
    local domain=$1
    local check_script=$2
    local timeout=$3
    local script_name=$(basename "$check_script" .sh)
    if ! timeout "$timeout" bash "$check_script" "$domain"; then
        echo "ERROR: $script_name failed for $domain after $timeout seconds"
    fi
}


if [ "$CHECK_TYPE" == "help" ]; then
    help
    exit 0
if [[ "$CHECK_TYPE" != "$ALL" && "$CHECK_TYPE" != "$HTTP" && "$CHECK_TYPE" != "$SSL" && "$CHECK_TYPE" != "$WHOIS" ]]; then
    usage
    exit 1
fi

if [ -n "$USERNAME" ]; then
    # If a username is provided, find the user file that matches
    user_file="${USERS_DIR}${USERNAME}.json"
    if [ ! -f "$user_file" ]; then
        echo "ERROR: User file for username '$USERNAME' not found."
        exit 1
    fi
    DOMAINS=$(jq -r '.domains[].name' "$user_file")
else
    # If no username is provided, process all users
    for user_file in $USERS_DIR*.json; do
        DOMAINS=$(jq -r '.domains[].name' "$user_file")
    done
fi

for domain in $DOMAINS; do
    echo "$domain"
    case $CHECK_TYPE in
        $ALL)
            check_domain "$domain" "${SCRIPTS_DIR}/$HTTP.sh" 15
            check_domain "$domain" "${SCRIPTS_DIR}/$SSL.sh" 5
            check_domain "$domain" "${SCRIPTS_DIR}/$WHOIS.sh" 10
            ;;
        $HTTP)
            check_domain "$domain" "${SCRIPTS_DIR}/$HTTP.sh" 15
            ;;
        $SSL)
            check_domain "$domain" "${SCRIPTS_DIR}/$SSL.sh" 5
            ;;
        $SHOIS)
            check_domain "$domain" "${SCRIPTS_DIR}/$WHOIS.sh" 10
            ;;
        *)
            usage
            ;;
    esac
    echo "____________________________________________________________"
done
