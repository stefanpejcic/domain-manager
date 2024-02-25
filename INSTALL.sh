#!/bin/bash
# INSTALL.sh

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Update package list
apt update

# Install MySQL server
apt install mysql-server -y

# Install Python3 and Flask
apt install python3 -y
pip install Flask
pip install flask_sqlalchemy

# Install MySQL client
apt-get install python3-mysqldb

# Install additional dependencies
apt-get install pkg-config libmysqlclient-dev

# Install mysqlclient
pip install mysqlclient --global-option=build_ext --global-option="-I/usr/include/mysql" --global-option="-L/usr/lib/x86_64-linux-gnu -lmysqlclient"

# Start MySQL service
systemctl start mysql

# Create a MySQL database and switch to it
mysql -e "CREATE DATABASE IF NOT EXISTS domains;"
mysql -e "USE domains;"

# Import table structure from file
mysql domains < table_structure.sql

# Restart MySQL service
systemctl restart mysql
