# How to install the infralinker application.

## Table of Contents

- [1. OS Minimum Requirements](#os-minimum-requirements)
- [2. Packages Requirements](#packages-requirements)
- [3. Update Packages and installation](#update-packages-and-installation)
- [4. Create a new user](#create-a-new-user)
- [5. Lock down the firewall](#lock-down-the-firewall)
- [6. Disable or configure SELinux](#disable-or-configure-selinux)
- [7. Python and installation](#python-and-installation)
- [8. MariaDB installation and activation](#mariadb-installation-and-activation)
- [9. Nginx Installation](#nginx-installation)
- [10. Generate SSL certificate for HTTPS connection](#generate-ssl-certificate-for-https-connection)
- [11. Installing the program](#installing-the-program)
- [12. Edit the nginx config file](#edit-the-nginx-config-file)
- [13. Authentication to application](#authentication-to-application)

<a id="installation"></a>
# Installation
The installation instructions provided here have been tested to work on Rocky/CentOS 8/9 and Debian 12/13. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the Our Teams maintainers. Please consult your distribution's documentation for assistance with any errors.
<a id="os-minimum-requirements"></a>
### 1. OS Minimum Requirements
```
> Rockey / Centos / Debian.
> RAM : 6Gb
> CPU : 2
> DISQ : 50Gb
```
<a id="packages-requirements"></a>
### 2. Packages Requirements
```
dependency - minimum version
Python  - 3.10 >
MariaDB -  Last
Nginx - Last
```
<a id="update-packages-and-installation"></a>
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
<a id="create-a-new-user"></a>
### 4. Create a new user

```bash
$su - #to access with root user
$useradd -c "User For InfraLinker Solution"  infralinker
$passwd infralinker # Set Password to infralinker user
$gpasswd -a infralinker wheel  #to add infralinker to sudo users
```

<a id="lock-down-the-firewall"></a>
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

<a id="disable-or-configure-selinux"></a>
### 6. Disable Or configure selinux
```bash
$setenforce 0 #to disable selinux 

> or you can edit selinux config  file and change this value "SELINUX" to disabled
$sudo vi /etc/selinux/conf
~
SELINUX=disabled
```

<a id="python-and-installation"></a>
### 7. python and installation
**RPM Based OS**
```bash
$sudo yum install -y  python3.11 python3-pip git gcc gcc-c++  python3.11-devel  zlib-devel  libjpeg-devel
```

**DEP Based OS**
```bash
$sudo apt install python3-pip git gcc g++ python3-dev python3-venv zlib1g-dev libjpeg-dev python3-wheel
```

<a id="installing-uv-packages-management"></a>
**Installing uv packages management**

Before proceeding, ensure that the 'uv' package manager is installed. If it is not installed, you can install it using the following command (using wget):

```bash
$ wget -qO- https://astral.sh/uv/install.sh | sh
```

<a id="mariadb-installation-and-activation"></a>
### 8. mariadb installation and activation
```bash
$sudo yum install mariadb-server
$sudo systemctl start mariadb
$sudo systemctl enable mariadb
$sudo mariadb-secure-installation  #TO EDIT ROOT PASSWORD
```

<a id="nginx-installation"></a>
### 9. nginx Installation
**RPM Based OS**
```bash
$sudo yum install nginx
```
**DEB Based OS**
```bash
$sudo apt install nginx
```
<a id="generate-ssl-certificate-for-https-connection"></a>
### 10. Gen ssl certification for https connexion
```bash
$sudo dnf/apt update openssl
$sudo mkdir /etc/ssl/private
$sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt
```

<a id="installing-the-program"></a>
### 11. Installing the  program
Change the **admin_db** password in this two files.

install.sh **(line 41)**, export.sh **(line 7)** and nginx-conf/infralinkerd.service **(line 14)**

```bash
$su - infralinker
$cd /home/infralinker
$git clone https://github.com/Infralinker/Infralinker.git infralinker
$chown infralinker:nginx -R infralinker
$cd infralinker/
$echo -n "infralinker is the best project for dc management" | base64  #copy the output of this commande in instance/config.py at (STRIPE_API_KEY)
$chmod a+x *.sh 
$ ./instll.sh #This commande must be run as infralinker user
$ sudo ./web_install.sh #This commande must be run as sudo
```

<a id="edit-the-nginx-config-file"></a>
### 12. Edit the nginx config file.
```
Add your ip adresse or FQDN in the ligne N°4 and ligne N°23 in name_server parameter in /etc/nginx/conf.d/nginx-infralinker.conf .
$vi in /etc/nginx/conf.d/nginx-infralinker.conf 
```

<a id="authentication-to-application"></a>
### 13. Authentication to application
https://server_ip_adresse
login: admin@infralinker.com
password: ROOT1234

