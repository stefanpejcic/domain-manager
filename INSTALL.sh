#!/bin/bash
# INSTALL.sh

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Update package list
apt update

apt install mysql-server  pkg-config libmysqlclient-dev python3 python3-flask python3-mysqldb pip -y

pip install Flask flask_sqlalchemy --break-system-packages
pip install mysqlclient --global-option=build_ext --global-option="-I/usr/include/mysql" --global-option="-L/usr/lib/x86_64-linux-gnu -lmysqlclient" --break-system-packages

# Start MySQL service
systemctl start mysql

# Create a MySQL database and switch to it
mysql -e "CREATE DATABASE IF NOT EXISTS domains;"
mysql -e "USE domains;"

# Import table structure from file
mysql domains < table_structure.sql


# Create user 'manager' with password 'ds732bfsd' and grant all privileges on 'domains' database
mysql -e "CREATE USER IF NOT EXISTS 'manager'@'localhost' IDENTIFIED BY 'ds732bfsd';"
mysql -e "GRANT ALL PRIVILEGES ON domains.* TO 'manager'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Save the login info for bash scripts
cat > db.cnf <<EOF
[client]
user = "manager"
password = "ds732bfsd"
host = "localhost"
EOF

chown root:root db.cnf

# Restart MySQL service
systemctl restart mysql

# Make all bash script executable
chmod +x -R scripts/


# Set cron to check SSL status, HTTP response and WHOIS information
SCRIPT_PATH="/root/domain-manager-main/scripts/scheduler.sh"

# Prepare cron job lines
CRON_JOBS=(
    "*/5 * * * * $SCRIPT_PATH http_response_check"
    "0 0 * * * $SCRIPT_PATH ssl_check"
    "0 */6 * * * $SCRIPT_PATH whois_check"
)

# Backup current crontab
crontab -l > crontab_backup.txt

# Check and add each cron job if it doesn't already exist
for job in "${CRON_JOBS[@]}"; do
    crontab -l | grep -qF -- "$job" || (crontab -l; echo "$job") | crontab -
done

echo "Cron jobs added successfully."

echo ""
echo "flask run --host 0.0.0.0"
