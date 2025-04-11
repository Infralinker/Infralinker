#!/bin/bash

###############  FOURTH INSTALLATION  NGINX CONFIGURATION AND SERVICE INSTALLATION  ##########################
echo "wsgi and config files copie."
cp nginx-conf/wsgi.py .
cp nginx-conf/production.ini .
echo "Done"

echo "change the owner group of infralinker folder to nginx group."
chgrp nginx /home/infralinker -R

echo "Add nginx to infralinker group."
gpasswd -a nginx infralinker
echo "Create infralinker services."
cp nginx-conf/infralinkerd.service /etc/systemd/system/


echo "Enable and starting services..."
systemctl reload infralinkerd
systemctl enable infralinkerd
systemctl start infralinkerd

echo "nginx install config."
cp nginx-conf/nginx-infralinker.conf  /etc/nginx/conf.d/
sed -i 's/user nginx/user infralinker/' /etc/nginx/nginx.conf

systemctl enale nginx
systemctl start nginx