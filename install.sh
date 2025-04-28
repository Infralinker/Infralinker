#!/bin/bash
# Script Name: Setup infralinker
# Description: Combines and improves the first installation and dependencies checking for the Infralinker application.
# Author: Abdellah ALAOUI ISMAILI
# Version: 1.0.1

# Function to print progress bar
print_progress() {
    local current="$1"
    local total="$2"
    local length=50
    local percentage=$((current * 100 / total))
    local completed=$((percentage * length / 100))
    local remaining=$((length - completed))
    printf "["
    printf "%${completed}s" | tr ' ' '='
    printf "%${remaining}s" | tr ' ' '-'
    printf "] %d%%\r" "$percentage"
}

# Function to check if a package is installed using rpm (Red Hat-based systems)
is_package_installed_rpm() {
    local package_name="$1"
    rpm -q "$package_name" >/dev/null 2>&1
}

echo "###################################################################"
echo "### BEFORE STARTING, YOU MUST HAVE IP OR HOSTNAME OF YOUR SERVER ##"
echo "########## YOU MUST HAVE ROOT USER AND ROOT PASSWORD    ########"
echo "###################################################################"

read -p "Enter DB Server IP or Hostname: " db_host
read -p "Enter the root user: " db_root_user
read -s -p "Enter the root password: " db_password
echo ""

echo "Creating database and user..."
# Login to MySQL database and create database, user, and grant privileges
mysql -h $db_host -u $db_root_user -p$db_password << EOF
CREATE DATABASE IF NOT EXISTS infralinker_db;
<<<<<<< HEAD
CREATE USER IF NOT EXISTS 'admin_db'@'localhost' IDENTIFIED BY 'admin_db_password';
=======
CREATE USER IF NOT EXISTS 'admin_db'@'localhost' IDENTIFIED BY 'admin_password_her';
>>>>>>> 531040b1bf7d6e2cdc7b9c4ccedef51f5bf2e4b5
GRANT ALL PRIVILEGES ON infralinker_db.* TO 'admin_db'@'localhost';
exit
EOF

echo "Checking installed dependencies..."
# List of packages to check
packages=("python38" "python3-pip" "git" "gcc" "gcc-c++" "python38-devel" "python3-virtualenv" "zlib-devel" "libjpeg-devel" "python3-wheel")

# Check for package installation
progress_count=0
total_packages=${#packages[@]}
for package in "${packages[@]}"; do
    if is_package_installed_rpm "$package"; then
        echo "Package '$package' is installed."
    else
        echo "Package '$package' is NOT installed."
    fi
    ((progress_count++))
    print_progress "$progress_count" "$total_packages"
done
echo ""

echo "Creating a new virtual environment..."
python3 -m venv $HOME/infralinker_venv
source $HOME/infralinker_venv/bin/activate

echo "Upgrading pip to the latest version..."
pip install --upgrade pip

echo "Installing required packages from requirements.txt..."
pip install -r requirements.txt
pip install wheel

key_file="key.key"
if [ -f "$key_file" ]; then
    if [ -s "$key_file" ]; then
        key_content=$(<"$key_file")
    else
        echo "File '$key_file' exists but is empty."
    fi
else
    echo "File '$key_file' does not exist."
fi

echo "Exporting ENVs..."
source export.sh

echo "Initializing and migrating the database..."
flask db init
flask db migrate
flask db upgrade

deactivate

mysql -h $db_host -u $db_root_user -p$db_password << "EOF"
use infralinker_db;

# Insert initial data
INSERT IGNORE INTO departments VALUES (1, "IT", "IT Infrastructure Department");
INSERT IGNORE INTO admins (id, firstname, lastname, email, phone, function, password_hash, is_admin, is_manager, control_racks, control_platforms, control_networks, control_servers, control_applications, department_id, change_password, last_seen) VALUES 
(1, "Admin", "Administrator", "admin@infralinker.com", "060-000-0006", "Application Administrator", "pbkdf2:sha256:150000$5l5suuHR$b63b9521dbcf42e9a89cea7d03a51ae79fe3748f381f0dc24ffc11fd8b3b7b2b", 1, 1, 1, 1, 1, 1, 0, 1, 1, 0);

INSERT IGNORE INTO tags (id, tag_name, tag_description, tag_color, add_by, add_date) VALUES 
(1, "PROD", "PRODUCTION ENVIRONMENT", "#0B8C5A", "1", "31-12-2020"),
(2, "TEST", "TEST ENVIRONMENT", "#F252D2", "1", "31-12-2020"),
(3, "DMZ", "DEMILITARIZED ZONE", "#CCF3FF", "1", "31-12-2020"),
(4, "PRIV", "PRIVATE ZONE", "#DD6E88", "1", "31-12-2020"),
(5, "PUBL", "PUBLIC ZONE", "#4B0170", "1", "31-12-2020");

INSERT IGNORE INTO device_roles (id, name, description, device_color) VALUES
(1, "SW SAN", "SWITCH SAN", "#e5bb90"),
(2, "SW TOR", "TOR SWITCH", "#079653"),
(3, "SW LAN", "SWITCH LA", "#04c994"),
(4, "NAS", "Network Attached Storage", "#ef4750"),
(5, "LB", "LOAD BALANCER", "#a088f7"),
(6, "FW PALO", "FIREWALL PALO ALT", "#9eef97"),
(7, "INTEL", "SERVER INTEL", "#9fbae0"),
(8, "POWER", "SERVER POWER", "#71bf39"),
(9, "FW ASA", "FIREWALL CISCO ASA", "#b19ff2"),
(10, "ROUTER", "ROUTER", "#4c6bad");

# Create Views
CREATE VIEW IF NOT EXISTS platforms_warranty AS
SELECT id, platform_name, end_warranty_date, "OUT" AS STATUS 
FROM platforms WHERE DATE(end_warranty_date) < DATE(SYSDATE())
UNION ALL
SELECT id, platform_name, end_warranty_date, "IN" AS STATUS 
FROM platforms WHERE DATE(end_warranty_date) > DATE(SYSDATE());

CREATE VIEW IF NOT EXISTS contract_validity AS
SELECT id, contract_number, start_date, end_date, "EXPIRED" AS STATUS 
FROM contracts WHERE DATE(end_date) < DATE(SYSDATE())
UNION ALL
SELECT id, contract_number,start_date, end_date, "VALID" AS STATUS 
FROM contracts WHERE DATE(end_date) > DATE(SYSDATE());

exit
EOF

echo "Installation completed successfully."
