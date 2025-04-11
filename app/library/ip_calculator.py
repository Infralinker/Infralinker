#!/usr/bin/env python3
import sys,ipaddress
from ..models import Network
from flask import flash
import datetime

def get_subnet(ip,mask):
    try:
        host = ipaddress.IPv4Address(ip)
        net = ipaddress.IPv4Network(ip + '/' + mask, False)
        subnet = ipaddress.IPv4Address(int(host) & int(net.netmask))
        return subnet
    except ValueError:
        flash('address/netmask is invalid for IPv4:')

def get_total_hosts(ip, mask):
    try:
        host = ipaddress.IPv4Address(ip)
        net = ipaddress.IPv4Network(ip + '/' + mask, False)
        total_hosts =  int(net.broadcast_address) - int(host)
    # return net.num_addresses (this is correct to if using from gatwey to the end of range)
        return total_hosts
    except ValueError:
        flash('address/netmask is invalid for IPv4:')

def get_ip_range(ip, mask):
    try:
        ip_range=[]
        host = ipaddress.IPv4Address(ip)
        net = ipaddress.IPv4Network(ip + '/' + mask, False)
        ip_range.append(host+1)
        ip_range.append(net.broadcast_address)
        return ip_range
    except ValueError:
        flash('address/netmask is invalid for IPv4:')

def get_cidr(ip, mask):
    # host = ipaddress.IPv4Address(ip)
    try:
        net = ipaddress.IPv4Network(ip + '/' + mask, False)
        return net.prefixlen
    except ValueError:
        flash('address/netmask is invalid for IPv4:')

def check_ip_in_network(server_ip, ip, mask):
    server = ipaddress.IPv4Address(server_ip)
    net = ipaddress.IPv4Network(ip + '/' + mask, False)
    return server in net

def check_ip_in_network_by_id(tag_network, server_ip):
    network = Network.query.get_or_404(tag_network)
    server = ipaddress.IPv4Address(server_ip)
    subnet =  get_subnet(network.gatway, network.mask)
    cidr = get_cidr(network.gatway, network.mask)
    net = ipaddress.IPv4Network(str(subnet) + '/' + str(cidr), False)

    if server in net :
        return True
    else :
        return False

#CHECK EXPIRATION IN 3MOUNTH
def check_expiration_date(end_date):
    time_between_insertion = end_date - datetime.date.today()

    if  90 > time_between_insertion.days > 1 :
        return 3 #Expire in less then 3 mount
    elif time_between_insertion.days <= 1 :
        return 0
    else:
        return 1 