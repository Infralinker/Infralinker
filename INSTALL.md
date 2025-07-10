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
### 2. Packages Requirements
```
dependency - minimum version
Python  - 3.10 >
MariaDB -  Last
Nginx - Last
```
### 3. Update Packages and installation
**RPM Based OS**
```bash
$sudo yum update
$sudo yum install epel-release
```
**DEB Based OS**
```bash
$sudo apt update
```
### 4. Create a new user

```bash
$su - #to access with root user
$useradd -c "User For InfraLinker Solution"  infralinker
$passwd infralinker # Set Password to infralinker user
$gpasswd -a infralinker wheel  #to add infralinker to sudo users
```

### 5. lock Down the firewall
**ALLOW INCOMING CONNECTIONS ON WEB PORTS USING HTTPS ONLY**

**RPM Based OS**
```bash
$su -
$export WHITELIST_IPADDR=0.0.0.0
$systemctl enable firewalld
$systemctl start firewalld
$firewall-cmd --zone=public --add-service=https --permanent
$firewall-cmd --zone=trusted --add-source=${WHITELIST_IPADDR} --permanent
$firewall-cmd --reload
```
**DEB Based OS**
```bash
$export WHITELIST_IPADDR=0.0.0.0
$sudo ufw enable
$sudo ufw allow https
$sudo ufw allow from ${WHITELIST_IPADDR}
$sudo ufw reload
```

### 6. Disable Or configure selinux
```bash
$setenforce 0 #to disable selinux 

> or you can edit selinux config  file and change this value "SELINUX" to disabled
$sudo vi /etc/selinux/conf
~
SELINUX=disabled
```

### 7. python and installation
**RPM Based OS**
```bash
$sudo yum install -y  python3.11 python3-pip git gcc gcc-c++  python3.11-devel  zlib-devel  libjpeg-devel
```

**DEP Based OS**
```bash
$sudo apt install python3-pip git gcc g++ python3-dev python3-venv zlib1g-dev libjpeg-dev python3-wheel
```
### 8. mariadb installation and activation
```bash
$sudo yum install mariadb-server
$sudo systemctl start mariadb
$sudo systemctl enable mariadb
$sudo mariadb-secure-installation  #TO EDIT ROOT PASSWORD
```

### 9. nginx Installation
**RPM Based OS**
```bash
$sudo yum install nginx
```
**DEB Based OS**
```bash
$sudo apt install nginx
```
### 10. Gen ssl certification for https connexion
```bash
$sudo dnf/apt update openssl
$sudo mkdir /etc/ssl/private
$sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
```

### 11. Installing the  program
Change the **admin_db** password in this two files.

install.sh **(line 41)**, export.sh **(line 7)** and nginx-conf/infralinkerd.service **(line 14)**

```bash
$cd /home/infralinker
$git clone https://github.com/Infralinker/Infralinker.git infralinker
$chown infralinker:nginx -R infralinker
$cd infralinker/
$echo -n "infralinker is the best project for dc management" | base64  #copy the output of this commande in instance/config.py at (STRIPE_API_KEY)
$chmod a+x *.sh 
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

