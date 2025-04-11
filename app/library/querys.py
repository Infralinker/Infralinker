#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Author: Abdellah ALAOUI ISMAILI
#   
#  Project Name: InfraLinker
#  Project web Site: http://infralinker.net

"""
File Library Contain all necessary query for the app.
"""

from sqlalchemy import create_engine
import pandas as pd
import os
from flask import current_app

def mydc_db_connexion():
    db_connection_str = current_app.config["SQLALCHEMY_DATABASE_URI"]
    db_connection = create_engine(db_connection_str)
    return db_connection
mydc_db = mydc_db_connexion()

#THIS QUERY IS FOR GETTING TOTAL IP FROM SELECTED DATACENCER (DONE)
def query_count_ip_dc(id_dc):
    query_result = pd.read_sql("""SELECT COUNT(*)ip
                                FROM datacenters, networks , servers
                                WHERE datacenters.id = networks.datacenter_id                                
                                AND networks.id = servers.network_id
                                AND  datacenters.id = '%i'
                                GROUP BY datacenters.dc_name""" % id_dc, con=mydc_db)
    return query_result

#THIS QUERY IS FOR GETTING TOTAL RACK FROM SELECTED DATACENCER  (DONE)
def query_count_rack_dc(id_dc):
    query_result = pd.read_sql("""SELECT COUNT(*)rack
                                FROM datacenters, racks
                                WHERE datacenters.id = racks.datacenter_id
                                AND datacenters.id = '%i'
                                """ % id_dc, con=mydc_db)
    return query_result

#THIS QUERY IS FOR GETTING TOTAL USED U IN RACK FROM SELECTED DATACENCER (DONE)
def query_count_u_dc(id_dc):
    query_result = pd.read_sql("""SELECT SUM(platforms.u_hight) AS sum_u
                                FROM datacenters, racks, platforms 
                                WHERE datacenters.id = racks.datacenter_id
                                AND racks.id = platforms.rack_id
                                AND datacenters.id = '%i'
                                """ % id_dc, con=mydc_db)
    return query_result

#THIS QUERY IS FOR GETTING TOTAL TICKET FROM SELECTED DATACENCER  (DONE)
def query_count_ticket_dc(id_dc):
    query_result = pd.read_sql("""SELECT COUNT(*)ticket
                                FROM datacenters, platforms, racks , tickets
                                WHERE datacenters.id = racks.datacenter_id
                                AND racks.id = platforms.rack_id
                                AND platforms.id = tickets.platform_id
                                AND datacenters.id = '%i'
                                GROUP BY datacenters.dc_name""" % id_dc, con=mydc_db)
    return query_result

#THIS QUERY IS FOR GETTING TOTAL VLAN/NETWORK FROM SELECTED DATACENCER  (DONE)
def query_count_network_dc(id_dc):
    query_result = pd.read_sql("""SELECT count(DISTINCT networks.id)
                                FROM datacenters,networks
                                WHERE datacenters.id = networks.datacenter_id
                                AND datacenters.id = '%i'
                                GROUP BY datacenters.dc_name""" % id_dc, con=mydc_db)
    return query_result

#THIS QUERY TO GET TICKETS BY STATUS (DONE)
def query_tickets_status() :
    query_result = pd.read_sql ("""
            SELECT COUNT(*)count_status, status 
            FROM tickets 
            GROUP BY status""", con = mydc_db)
    return query_result

#THIS QUERY TO GET TICKETS BY RESPONSABLE USER (DONE)
def query_tickets_by_user() :
    query_result= pd.read_sql("""
            SELECT COUNT(*) AS count_user, admins.lastname AS name
            FROM tickets, admins 
            WHERE admins.id = tickets.admin_id 
            GROUP BY admins.lastname""", con = mydc_db)
    return query_result

#QUERY TO GET  TICKETS BY SUPPLIERS (DONE)
def query_tickets_by_supplier() :
    query_result= pd.read_sql("""
            SELECT COUNT(*) AS count_supplier, suppliers.company_name AS company_name
            FROM tickets, suppliers 
            WHERE suppliers.id = tickets.supplier_id 
            GROUP BY suppliers.company_name""", con = mydc_db)
    return query_result

#THIS IS FOR OPEN TICKETS BY PLATFORM (DONE)
def query_tickets_by_platform() :
    query_result= pd.read_sql("""
            SELECT COUNT(*) AS count_platform, platforms.platform_name AS platform_name
            FROM tickets, platforms 
            WHERE platforms.id = tickets.platform_id 
            GROUP BY platforms.platform_name""", con = mydc_db)
    return query_result

#THIS QUERY CAN EXTRACT CONSUMED IP IN EACH DATACENTER (DONE)
def query_total_ip_by_datacenter() :
    query_result= pd.read_sql("""
    SELECT COUNT(servers.ip_address) AS total_ip, datacenters.dc_name AS dc_name
            FROM datacenters, networks, servers
            WHERE datacenters.id = networks.datacenter_id
            AND networks.id = servers.network_id
            GROUP BY datacenters.dc_name""", con=mydc_db)           
    return query_result

#THIS QUERY FOR GETING TOTAL OF NETWORKS BY DATACENTER (DONE)
def query_total_network_by_datacenter() :
    query_result = pd.read_sql("""
            SELECT COUNT(*) AS total_network, datacenters.dc_name AS dc_name
            FROM datacenters, networks
            WHERE datacenters.id = networks.datacenter_id
            GROUP BY datacenters.dc_name""", con=mydc_db)
    return query_result

#CALCULAT NUMBER OF CONSUED U IN EACH DATACENTER (DONE)
def query_sum_u_by_datacenterc():
    query_result = pd.read_sql("""
                    SELECT SUM(platforms.u_hight) AS sum_u, datacenters.dc_name
                    FROM datacenters, racks, platforms 
                    WHERE datacenters.id = racks.datacenter_id
                    AND racks.id = platforms.rack_id
                    GROUP BY datacenters.dc_name
        """, con=mydc_db)
    return query_result

#CALCULAT THE NUMBER OF RACKS GROUPED BY DATACENTER (DONE)
def query_count_racks_by_dc():
    query_result = pd.read_sql("""
                    SELECT COUNT(racks.id) AS count_racks, datacenters.dc_name AS dc_name
                    FROM racks, datacenters
                    WHERE datacenters.id = racks.datacenter_id
                    GROUP BY datacenters.dc_name
        """, con=mydc_db)
    return query_result

def query_total_all_networks():
    query_result = pd.read_sql("""
        SELECT COUNT(*) AS total_networks FROM networks""", con=mydc_db)
    return query_result

def query_total_all_servers():
    query_result = pd.read_sql("""
        SELECT COUNT(*) AS total_servers FROM servers""", con=mydc_db)
    return query_result

#COUNT OPEN VULNERABILITY BY STATUS, DC (DONE)
def query_open_vulnerabilities():
    query_result = pd.read_sql("""
       SELECT COUNT(*) AS open_vulnerabilities 
       FROM vulnerabilities, tickets 
       WHERE tickets.id = vulnerabilities.ticket_id 
       AND tickets.status= "OPEN" """, con=mydc_db)
    return query_result

def query_open_vulnerabilities_by_dc():
    query_result = pd.read_sql("""
    SELECT COUNT(*) open_vulnerabilities , datacenters.dc_name as dcenter_name
    FROM tickets, datacenters, platforms, racks, vulnerabilities
    WHERE datacenters.id = racks.datacenter_id
    AND racks.id = platforms.rack_id
    AND platforms.id = tickets.platform_id
    AND tickets.id = vulnerabilities.ticket_id
    AND tickets.status="OPEN"
    GROUP BY datacenters.dc_name """, con=mydc_db)
    return query_result

def query_count_open_vulnerabilities_by_dc(id_dc):
    query_result = pd.read_sql("""
    SELECT COUNT(*) open_vulnerabilities 
    FROM tickets, datacenters, platforms, racks, vulnerabilities
    WHERE datacenters.id = racks.datacenter_id
    AND racks.id = platforms.rack_id
    AND platforms.id = tickets.platform_id
    AND tickets.id = vulnerabilities.ticket_id
    AND tickets.status="OPEN"
    AND datacenters.id = '%i'; """ % id_dc, con=mydc_db)
    return query_result 

def query_vulnerabilities_status():
    query_result = pd.read_sql("""
       SELECT COUNT(*) AS count_vulnerability, tickets.status AS ticket_status
        FROM vulnerabilities, tickets
        WHERE vulnerabilities.ticket_id = tickets.id 
        GROUP BY tickets.status """, con=mydc_db)
    return query_result

def query_open_tickets():
    query_result = pd.read_sql("""
    SELECT COUNT(*) AS open_tickets FROM tickets WHERE STATUS = "OPEN"
        """, con=mydc_db)
    return query_result

def query_open_projects():
    query_result = pd.read_sql("""
    SELECT COUNT(*) open_projects 
    FROM projects WHERE `status`= "progress"
        """, con=mydc_db)
    return query_result

#CALCULATE THE NUMBER OF IN/OUT WARRANTY PLATFORMS
def query_status_warranty_platform():
    query_result = pd.read_sql("""
    SELECT COUNT(*) AS w_status , status   
    FROM platforms_warranty GROUP BY status
        """, con=mydc_db)
    return query_result

# COUNT SERVERS BY VITALITY CLASSIFICATIONS
def query_servers_vitality_classification_():
    query_result = pd.read_sql(""" 
    SELECT COUNT(*) AS count_servers , vitality_classification 
    FROM  servers 
    GROUP BY vitality_classification
        """, con=mydc_db)
    return query_result

# PLATFOMRS WITH U POSITION IN RACK
def query_pname_u_position(id_rack):
    query_result = pd.read_sql(""" 
    SELECT platform_name, u_position 
    FROM platforms WHERE rack_id = '%i'
        """ % id_rack, con=mydc_db)
    return query_result

# QUERY TO GET MORE DETAILS ABOUT RACK
def query_details_rack(id_rack):
    query_result = pd.read_sql("""
    SELECT r_name,ru_hight, r_notes , racks.tags,racks.r_position, dc_name as localisation, dc_type as datacenter_type, count(*) as total_platform, SUM(u_hight) AS used_units, SUM(power_supply) As total_power, ru_hight - SUM(u_hight) AS free_units  
    FROM racks, datacenters, platforms
    WHERE datacenters.id = racks.datacenter_id
    AND racks.id = platforms.rack_id
    AND rack_id = '%i'
    GROUP BY racks.r_name;
        """ % id_rack, con=mydc_db)
    return query_result

#CALCULATE THE NUMBER OF IN/OUT CONTRACTS
def query_contracts_status():
    query_result = pd.read_sql("""
    SELECT COUNT(*) AS contract_status , status   
    FROM contract_validity GROUP BY status
        """, con=mydc_db)
    return query_result

#COUNT PROJECT BY STATUS
def query_count_project_by_status(pj_statut):
    query_result = pd.read_sql("""
    SELECT COUNT(*) open_poject FROM projects WHERE status='%s' group by status;
        """ % pj_statut, con=mydc_db)
    return query_result

# QUERY MODELE
def query_get_tag_color(tg_name):
    query_result = pd.read_sql("""
    SELECT tag_color FROM tags where tag_name='%s';
        """ % tg_name, con=mydc_db)
    return query_result

#QUERY MODELE
def query_list_actions_for_project(id_project):
    query_result = pd.read_sql("""
    SELECT id, description, execution_date, finish_date, status 
    FROM actions WHERE project_id = '%i';
        """ % id_project, con=mydc_db)
    return query_result

######## LAST CREATED QUERY 2023 ########
# QUERY COUNT STATUS TICKET BY GIVEN DC ID
def query_ticket_status_by_id_dc(id_dc):
    query_result = pd.read_sql("""
    SELECT COUNT(*) as status_count , tickets.status as status
    FROM tickets, datacenters, platforms, racks
    WHERE datacenters.id = racks.datacenter_id
    AND racks.id = platforms.rack_id
    AND platforms.id = tickets.platform_id
    AND datacenters.id = '%i'
    GROUP BY tickets.status;
        """ % id_dc, con=mydc_db)
    return query_result

#QUERY FOR TOP 10 USED NETWORKS BY DATACENTER
def query_top_used_networks_by_id_dc(id_dc):
    query_result = pd.read_sql("""
    SELECT COUNT(*) as servers , networks.net_name as name
    FROM networks, servers, datacenters
    WHERE datacenters.id = networks.datacenter_id
    AND networks.id = servers.network_id
    AND datacenters.id = '%i'
    GROUP BY networks.net_name
    desc LIMIT 10;
        """ % id_dc, con=mydc_db)
    return query_result

# SERVER VITALITY COUNT BY DATACENTER
def query_server_vitality_count_by_id_dc(id_dc):
    query_result = pd.read_sql("""
    SELECT COUNT(*) as servers, servers.vitality_classification AS vitality
    FROM servers, networks, datacenters
    WHERE datacenters.id = networks.datacenter_id
    AND networks.id = servers.network_id
    AND datacenters.id = '%i'
    GROUP BY servers.vitality_classification;
        """ % id_dc , con=mydc_db)
    return query_result

# TYPE SERVERS BY DATACENTER
def query_server_type_count_by_id_dc(id_dc):
    query_result = pd.read_sql("""
    SELECT COUNT(*) servers, servers.type as type
    FROM servers, networks, datacenters
    WHERE datacenters.id = networks.datacenter_id
    AND networks.id = servers.network_id
    AND datacenters.id = '%i'
    GROUP BY servers.type;
        """ % id_dc , con=mydc_db)
    return query_result


#QUERY DEVICE ROLE BY DATACENTER
def query_device_role_count_by_id_dc(id_dc):
    query_result = pd.read_sql("""
    SELECT COUNT(*) as device_count , device_roles.name as name
    FROM device_roles, platforms, racks, datacenters
    WHERE racks.datacenter_id = datacenters.id
    AND platforms.rack_id = racks.id
    AND device_roles.id = platforms.device_role_id
    AND datacenters.id = '%i'
    GROUP BY device_roles.name
        """  % id_dc  , con=mydc_db)
    return query_result

#QUERY VULNERABILITIES BY DATACENTER
def query_vulnerability_status_by_id_dc(id_dc):
    query_result = pd.read_sql("""  
    SELECT COUNT(*) AS count_vlty, tickets.status as status
    FROM tickets, datacenters, platforms, racks, vulnerabilities
    WHERE datacenters.id = racks.datacenter_id
    AND racks.id = platforms.rack_id
    AND platforms.id = tickets.platform_id
    AND tickets.id = vulnerabilities.ticket_id
    AND datacenters.id = '%i'
    GROUP BY tickets.status
        """   % id_dc , con=mydc_db)
    return query_result

#QUERY TO COUNT TICKETS STATUS BY SUPPLIERS (USED).
def query_count_ticket_status_by_supplier():
    query_result = pd.read_sql("""
    SELECT COUNT(*) AS count_tickets , tickets.status AS status, suppliers.company_name AS company
    FROM tickets, suppliers
    WHERE suppliers.id = tickets.supplier_id
    AND tickets.status = "OPEN"
    GROUP BY suppliers.company_name , tickets.status
        """, con=mydc_db)
    return query_result

#QUERY TO COUNT TICKETS STATUS BY SUPPLIER ID USED IN SUPPLIERS DETAILS (USED).
def query_count_ticket_status_by_supplier_id(id_supplier):
    query_result = pd.read_sql("""
    SELECT COUNT(*) AS count_tickets , tickets.status AS status
    FROM tickets, suppliers
    WHERE suppliers.id = tickets.supplier_id
    AND suppliers.id = "%i"
    GROUP BY tickets.status
        """ % id_supplier, con=mydc_db)
    return query_result

#QUERY MODELE
# def query___():
#     query_result = pd.read_sql("""
#         """, con=mydc_db)
#     return query_result