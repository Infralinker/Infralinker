#!/bin/bash
# Script Name: Remove infralinker
# Description: Uninstall Infralinker application.
# Author: Abdellah ALAOUI ISMAILI
# Version: 1.0.1

if [ "$EUID" -ne 0 ]
      then echo "Please run this script as root"
      exit
else
      read -p "Enter DB Server IP or Hostname : " db_host
      read -p "Enter the root user : " db_root_user
      read -s "Enter the root password: " db_password

      ############# STOP AND DISABLE ALL SERVICES #################

      systemctl disable infralinkerd
      systemctl stop infralinkerd

      systemctl disable nginx
      systemctl stop nginx

      rm -fr /etc/systemd/system/infralinkerd.service
      rm -fr /etc/nginx/conf.d/nginx-infralinker.conf
      sed -i 's/user infralinker/user nginx/' /etc/nginx/nginx.conf

      ############## REMOVE DATA BASES ######################
      #Connexion to Database
      mysql -h $db_host -u $db_root_user -p$db_password << EOF

      ### DROP DB
      DROP DATABASE infralinker_db;

      exit
EOF

      ########## REMOVE ENVIRONEMENT ####################

      rm -fr /home/infralinker/infralinker_venv

fi