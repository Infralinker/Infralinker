#!/bin/bash
# Script Name: Remove infralinker
# Description: Uninstall Infralinker application.
# Author: Abdellah ALAOUI ISMAILI
# Version: 1.0.2

set -euo pipefail

function require_root() {
      if [ "$EUID" -ne 0 ]; then
            echo "Please run this script as root" >&2
            exit 1
      fi
}

function prompt_db_credentials() {
      read -rp "Enter DB Server IP or Hostname: " db_host
      read -rp "Enter the root user: " db_root_user
      read -srp "Enter the root password: " db_password
      echo
}

function stop_and_disable_services() {
      for svc in infralinkerd nginx; do
            if systemctl is-active --quiet "$svc"; then
                  systemctl stop "$svc"
            fi
            if systemctl is-enabled --quiet "$svc"; then
                  systemctl disable "$svc"
            fi
      done
}

function remove_service_files() {
      [ -f /etc/systemd/system/infralinkerd.service ] && rm -f /etc/systemd/system/infralinkerd.service
      [ -f /etc/nginx/conf.d/nginx-infralinker.conf ] && rm -f /etc/nginx/conf.d/nginx-infralinker.conf
      if grep -q 'user infralinker' /etc/nginx/nginx.conf; then
            sed -i 's/user infralinker/user nginx/' /etc/nginx/nginx.conf
      fi
}

function remove_database() {
      echo "Dropping infralinker_db database..."
      mysql -h "$db_host" -u "$db_root_user" -p"$db_password" <<EOF
DROP DATABASE IF EXISTS infralinker_db;
EOF
}

function remove_environment() {
      venv_path="/home/infralinker/infralinker/.venv"
      if [ -d "$venv_path" ]; then
            rm -rf "$venv_path"
            echo "Removed virtual environment at $venv_path"
      fi
}

# Main execution
require_root
prompt_db_credentials
stop_and_disable_services
remove_service_files
remove_database
remove_environment

# Remove all uv packages and binaries
echo "Removing all uv packages and binaries..."
uv cache clean || true
rm -rf "$(uv python dir)" || true
rm -rf "$(uv tool dir)" || true
rm -f ~/.local/bin/uv ~/.local/bin/uvx || true

echo "Infralinker uninstallation complete."