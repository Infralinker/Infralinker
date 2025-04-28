# How to install the infralinker application.
## I. installation
The installation instructions provided here have been tested to work on Rocky Linux 9 and CentOS 8 and 9. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the Our Teams maintainers. Please consult your distribution's documentation for assistance with any errors.

### 1. OS Minimum Requirements
```
> rockey linux +8.0, centos +7.0, redhat +7.0.
> RAM : 6Gb
> CPU : 2
> DISQ : 50Gb
```
### 2. packages Requirements
```
dependency - minimum version
Python  - 3.8 >
MariaDB -  5.5 >
Nginx - Last
```
### 3. update Packages and installation epel
```bash
$sudo yum update
$sudo yum install epel-release
```
### 4. create A new user

```bash
$su - #to access with root user
$useradd -c "User For InfraLinker Solution"  infralinker
$passwd infralinker # Set Password to infralinker user
$gpasswd -a infralinker wheel  #to add infralinker to sudo users
```

### 5. lock Down the firewall

```bash
#ALLOW INCOMING CONNECTIONS ON WEB PORTS USING HTTPS ONLY
$su -
$export WHITELIST_IPADDR=0.0.0.0
$systemctl enable firewalld
$systemctl start firewalld
$firewall-cmd --zone=public --add-service=https --permanent
$firewall-cmd --zone=trusted --add-source=${WHITELIST_IPADDR} --permanent
$firewall-cmd --reload
```

### 6. disable Or configure selinux
```bash
$setenforce 0 #to disable selinux 

> or you can edit selinux config  file and change this value "SELINUX" to disabled
$sudo vi /etc/selinux/conf
~
SELINUX=disabled
```

### 7. python3.8 installation

```bash
$sudo yum install -y  python38 python3-pip git gcc gcc-c++  python38-devel  python3-virtualenv  zlib-devel  libjpeg-devel  python3-wheel
```
>NB : DO NOT install python-virtualenv

### 8. mariadb 5.5 installation and activation
```bash
$sudo yum install mariadb-server
$sudo systemctl start mariadb
$sudo systemctl enable mariadb
$sudo mysql_secure_installation #TO EDIT ROOT PASSWORD
```

### 9. nginx Installation
```bash
$sudo yum install nginx
```

### 10. Gen ssl certification for https connexion
```bash
$sudo dnf update openssl
$sudo mkdir /etc/ssl/private
$sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
```

### 11. Installing the  program
change the admin_db password in this two files
<<<<<<< HEAD
install.sh (line 41) and nginx-conf/infralinkerd.service (line 14)
=======
install.sh and instance/config.py
>>>>>>> 531040b1bf7d6e2cdc7b9c4ccedef51f5bf2e4b5

```bash
$cd /home/infralinker
$git clone https://github.com/Infralinker/Infralinker.git infralinker
$chown infralinker:nginx -R infralinker
$cd infralinker/
$echo -n "infralinker is the best project for dc management" | base64  #copy the output of this commande in instance/config.py at (STRIPE_API_KEY)
<<<<<<< HEAD
$chmod a+x *.sh 
=======
$chmod a+x *.sh
>>>>>>> 531040b1bf7d6e2cdc7b9c4ccedef51f5bf2e4b5
$ ./instll.sh #This commande must be run as infralinker user
$ sudo ./web_install.sh #This commande must be run as sudo
```

### 12. Edit the nginx config file.
```
Add your ip adresse or FQDN in the ligne N°4 and ligne N°23 in name_server parameter in /etc/nginx/conf.d/nginx-infralinker.conf .
$vi in /etc/nginx/conf.d/nginx-infralinker.conf 
```

### 13. Authentication to application
https://server_ip_adresse
login: admin@infralinker.com
password: ROOT1234

