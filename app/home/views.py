#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Author: Abdellah ALAOUI ISMAILI
#   
#  Project Name: InfraLinker
#  Project web Site: http://infralinker.net
"""
This view file containing the home view functions for InfraLinker App, routes and the map to navigate in app.
"""

from flask import abort, render_template, request
from flask_login import current_user, login_required
from . import home
from ..models import Admin, Supplier, Ticket, Platform, Vulnerability, Intervention, Project, Action, Datacenter,Rack, Network,Server
import pandas as pd
import json
import plotly
import plotly.express as px
from ..library.querys import mydc_db_connexion, query_count_ip_dc, query_count_u_dc, query_count_rack_dc, query_count_ticket_dc, query_count_network_dc, query_tickets_by_supplier,\
 query_tickets_by_platform, query_tickets_status, query_tickets_by_user, query_total_ip_by_datacenter, query_total_network_by_datacenter,\
 query_total_all_networks, query_total_all_servers, query_open_vulnerabilities,query_open_vulnerabilities_by_dc, \
 query_vulnerabilities_status,query_open_tickets, query_open_projects, query_count_racks_by_dc, query_total_ip_by_datacenter,\
 query_status_warranty_platform, query_contracts_status, query_count_open_vulnerabilities_by_dc, query_count_project_by_status, \
 query_ticket_status_by_id_dc, query_top_used_networks_by_id_dc , query_server_vitality_count_by_id_dc, query_server_type_count_by_id_dc, query_device_role_count_by_id_dc, \
 query_vulnerability_status_by_id_dc , query_count_ticket_status_by_supplier

import plotly.graph_objects as go
from ..library.emailling import get_cloud_provider_details

#This is the unified margin values of all chart.
chart_margin_values = {'t': 10, 'l': 20, 'b': 30, 'r': 40}
pie_chart_unified_legende = dict(orientation="h", yanchor="bottom",y=1, xanchor="left", x=0)

@home.route('/', methods=['GET'])
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/documentations/help', methods=['GET'])
def help():
    """
    Render the documentation template
    """
    return render_template('documentations/index.html', title="InfraLinker Documentations")

@home.route('/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    datacenters = Datacenter.query.all()   
            
    return render_template('admin/dashboard.html', title="Admin Dashboard",
                           query_count_ip_dc=query_count_ip_dc,
                           query_count_rack_dc=query_count_rack_dc,
                           query_count_u_dc=query_count_u_dc,
                           query_count_ticket_dc=query_count_ticket_dc,
                           query_open_projects = query_open_projects,
                           query_total_all_networks=query_total_all_networks,
                           query_total_all_servers=query_total_all_servers,
                           query_open_vulnerabilities=query_open_vulnerabilities,
                           query_open_tickets=query_open_tickets,
                           get_cloud_provider_details=get_cloud_provider_details,
    datacenters=datacenters)


@home.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():    
    # if not current_user.is_admin:        
        # abort(403)

    # if not current_user.is_manager:        
    #     abort(403)
    if not current_user.is_authenticated:        
        abort(403)
        
    datacenters = Datacenter.query.all()   

    last_open_tickets = Ticket.query.order_by(Ticket.open_date.desc()).filter(Ticket.status.like("OPEN")).limit(8).all()
    last_open_vulnerabilities = Vulnerability.query.order_by(Vulnerability.date_vulnerability.desc()).limit(6).all()
       
    # PRIMARY DASHBOARD : UNPATCHED VULNERABILITIES FOR ALL
    colors=["#66BFBF","#7A86B6","#1F4690"]
    labels_open_vulnerabily_dc = query_open_vulnerabilities_by_dc()["dcenter_name"]
    values_open_vulnerabily_dc = query_open_vulnerabilities_by_dc()["open_vulnerabilities"]
    figOpenVulnerbilitiesDC = go.Figure(data=[go.Pie(labels=labels_open_vulnerabily_dc, 
    hole =.5, marker=dict(colors=colors, line=dict(color='#FFFFFF', width=5)),
    values=values_open_vulnerabily_dc, title = '<span style="font-size: 16px;">OPEN<br>VULNERABILITIES</span>')])
    figOpenVulnerbilitiesDC.update_layout(margin=chart_margin_values)
    figOpenVulnerbilitiesDC.update_layout(legend=pie_chart_unified_legende)
    graphOpenVulnerabilitiesDC = json.dumps(figOpenVulnerbilitiesDC, cls=plotly.utils.PlotlyJSONEncoder)

    # PRIMARY DASHBOARD :  VULNERABILITIES STATUS FOR ALL DC
    colors=["#D61C4E","#7A86B6","#E8AA42"]
    labels_status_vulnerabily = query_vulnerabilities_status()["ticket_status"]
    values_status_vulnerabily = query_vulnerabilities_status()["count_vulnerability"]
    figVulnerbilitiesStat = go.Figure(data=[go.Pie(labels=labels_status_vulnerabily, 
    hole =.5,marker=dict(colors=colors, line=dict(color='#FFFFFF', width=4)),
    values=values_status_vulnerabily, title = '<span style="font-size: 16px;">VULNERABILITIES<br>STATUS</span>')])
    figVulnerbilitiesStat.update_layout(margin=chart_margin_values)
    figVulnerbilitiesStat.update_layout(legend=pie_chart_unified_legende)
    graphStatusVulnerabilities = json.dumps(figVulnerbilitiesStat, cls=plotly.utils.PlotlyJSONEncoder)

    # PRIMARY DASHBOARD :  OPEN TICKETS BY SUPPLIER
    labels_supplier = query_tickets_by_supplier()["company_name"]
    values_supplier = query_tickets_by_supplier()["count_supplier"]
    figSuppliers = go.Figure(data=[go.Pie(labels=labels_supplier, 
    hole =.5,marker=dict(line=dict(color='#FFFFFF', width=4)),
    values=values_supplier, title = '<span style="font-size: 18px;">BY SUPPLIER</span>')])
    figSuppliers.update_layout(margin=chart_margin_values)
    figSuppliers.update_layout(legend=pie_chart_unified_legende)
    graphTicketsSuppliers = json.dumps(figSuppliers, cls=plotly.utils.PlotlyJSONEncoder)
    
    labels_statut = query_tickets_status()['status']
    values_statut = query_tickets_status()['count_status']
    figStatus = go.Figure(data=[go.Pie(labels=labels_statut, values=values_statut, 
    hole=.5, marker=dict(line=dict(color='#FFFFFF', width=4)),
    title='<span style="font-size: 18px;">STATUS</span>')])
    figStatus.update_layout(margin=chart_margin_values)
    figStatus.update_layout(legend=pie_chart_unified_legende)
    figStatus.update_traces(textposition='inside', textinfo='percent+label')
    graphTicketsStatus = json.dumps(figStatus, cls=plotly.utils.PlotlyJSONEncoder)

    colors = ['gold', 'turquoise', 'orange', 'green']
    label_total_networks_dc = query_total_network_by_datacenter()['dc_name']
    values_total_networks_dc = query_total_network_by_datacenter()['total_network']
    figTTNetwork = go.Figure(data=[go.Pie(labels=label_total_networks_dc, values=values_total_networks_dc, 
    marker=dict(colors=colors, line=dict(color='#FFFFFF', width=4)),
    hole = 0.5, textposition='inside', textinfo='percent+value', text = values_total_networks_dc,
    title='<span style="font-size: 18px;">NETWORKs</span>' )])
    figTTNetwork.update_layout(margin=chart_margin_values)
    figTTNetwork.update_layout(legend=pie_chart_unified_legende)
    graphNetworkDataCenter = json.dumps(figTTNetwork, cls=plotly.utils.PlotlyJSONEncoder)

    colors = ['Blue' ,'Navy', 'Peach', 'Pink','Wedding']
    label_total_servers_dc = query_total_ip_by_datacenter()['dc_name']
    value_total_servers_dc = query_total_ip_by_datacenter()['total_ip']
    figTTServer = go.Figure(data=[go.Pie(labels=label_total_servers_dc, 
    marker=dict(colors=colors, line=dict(color='#FFFFFF', width=4)),
    values=value_total_servers_dc, hole = 0.5, text = value_total_servers_dc, 
    title='<span style="font-size: 18px;">IPs</span>' )])
    figTTServer.update_layout(margin=chart_margin_values)
    figTTServer.update_layout(legend=pie_chart_unified_legende)
    graphIPDataCenter = json.dumps(figTTServer, cls=plotly.utils.PlotlyJSONEncoder)

    fig_racks_by_dc = px.bar(query_count_racks_by_dc(), 
                                x='count_racks', y='dc_name',  color="dc_name",
                                labels = {'count_racks': 'RACKS', 'dc_name': 'DATACENTER NAME'},
                                text = 'count_racks',                                
                                title="TOTAL OF RACKS IN EACH DATACENTER")
    graphBar_racks_by_dc = json.dumps(fig_racks_by_dc, cls=plotly.utils.PlotlyJSONEncoder)

    colors = ['#C21010', '#CFE8A9']
    label_warranty_platforms = query_status_warranty_platform()['status']
    value_warranty_platforms = query_status_warranty_platform()['w_status']
    figWarrantyPlatform = go.Figure(data=[go.Pie(labels=label_warranty_platforms, values=value_warranty_platforms, 
    hole=.5,marker=dict(colors=colors, line=dict(color='#FFFFFF', width=4)),
    text = value_warranty_platforms, title='<span style="font-size: 16px;">DEVICE<br>STATUS</span>' )])
    figWarrantyPlatform.update_layout(margin=chart_margin_values)
    figWarrantyPlatform.update_layout(legend=pie_chart_unified_legende)
    figWarrantyPlatform.update_traces(textposition='inside', textinfo='percent+label')
    graphWarrantyPlatform = json.dumps(figWarrantyPlatform, cls=plotly.utils.PlotlyJSONEncoder)

    colors = ['#25316D', '#97D2EC']
    label_contracts = query_contracts_status()['status']
    value_contracts = query_contracts_status()['contract_status']
    figContractStatus = go.Figure(data=[go.Pie(labels=label_contracts, values=value_contracts, 
    hole=.5,marker=dict(colors=colors, line=dict(color='#FFFFFF', width=4)),
    text = value_contracts, title='<span style="font-size: 16px;">CONTRACTS<br>STATUS</span>' )])
    figContractStatus.update_layout(margin=chart_margin_values)
    figContractStatus.update_layout(legend=pie_chart_unified_legende)
    figContractStatus.update_traces(textposition='inside', textinfo='percent+label')
    graphContractStatus = json.dumps(figContractStatus, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    fig_tickets_by_suppliers = px.sunburst(query_count_ticket_status_by_supplier(), 
                                names ='company', 
                                parents = 'status',  
                                values ='count_tickets',
                                labels = {'count_tickets': 'COUNT TICKETS', 'company': 'COMPANY NAME', 'status':'TICKETS STATUS'})
    fig_tickets_by_suppliers.update_layout(margin=chart_margin_values)
    fig_tickets_by_suppliers.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.0))                                                      
    graphSunBurt_Tickes_by_Suppliers = json.dumps(fig_tickets_by_suppliers, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('admin/dashboard.html', title="Central Management  Dashboard",
                           query_count_ip_dc=query_count_ip_dc,
                           query_count_rack_dc=query_count_rack_dc,
                           query_count_ticket_dc=query_count_ticket_dc,

                           query_total_all_networks = query_total_all_networks,
                           query_total_all_servers = query_total_all_servers,
                           query_open_vulnerabilities = query_open_vulnerabilities,
                           query_open_tickets = query_open_tickets,
                           query_open_projects = query_open_projects,

                           last_open_tickets = last_open_tickets,
                           last_open_vulnerabilities = last_open_vulnerabilities,
                           
                           graphTicketsSuppliers=graphTicketsSuppliers,
                           graphTicketsStatus = graphTicketsStatus,
                           graphNetworkDataCenter = graphNetworkDataCenter,
                           graphIPDataCenter = graphIPDataCenter,
                           graphWarrantyPlatform=graphWarrantyPlatform,
                           graphContractStatus=graphContractStatus,
                           graphStatusVulnerabilities=graphStatusVulnerabilities,
                           graphOpenVulnerabilitiesDC=graphOpenVulnerabilitiesDC,
                           graphSunBurt_Tickes_by_Suppliers=graphSunBurt_Tickes_by_Suppliers,
                           get_cloud_provider_details=get_cloud_provider_details,

                           graphBar_racks_by_dc = graphBar_racks_by_dc,
                           datacenters=datacenters)


@home.route('/admin/detailed_dashboard/<int:id_datacenter>', methods=['GET'])
@login_required
def infos_datacenters(id_datacenter):
    """
    List all infos of selected datacenters
    """
    datacenters = Datacenter.query.all() #this is a defaults info in each datacenter keepit
    datacenter_name = Datacenter.query.get_or_404(id_datacenter)    #this is for getting th of selected datacenter
    
    count_ip_dc = query_count_ip_dc(id_datacenter)
    count_rack_dc = query_count_rack_dc(id_datacenter)
    count_ticket_dc = query_count_ticket_dc(id_datacenter)
    count_network_dc = query_count_network_dc(id_datacenter)
    count_u_dc = query_count_u_dc(id_datacenter)
    count_vul_by_dc = query_count_open_vulnerabilities_by_dc(id_datacenter)
    open_project = query_count_project_by_status('PROGRESS')
    close_project = query_count_project_by_status('COMPLETE')

    # TICKETS STATUS BY DATACENTER
    colors=["#FF7B54","#FFD56F","#ADA2FF"]
    labels_count_ticket_status_by_dc = query_ticket_status_by_id_dc(id_datacenter)["status"]
    values_count_ticket_status_by_dc = query_ticket_status_by_id_dc(id_datacenter)["status_count"]
    figCountTicktStatusByDC = go.Figure(data=[go.Pie(labels=labels_count_ticket_status_by_dc, 
    hole =.2, marker=dict(colors=colors, line=dict(color='#FFFFFF', width=5)),
    values=values_count_ticket_status_by_dc, title = '')])
    figCountTicktStatusByDC.update_layout(margin=chart_margin_values)
    figCountTicktStatusByDC.update_layout(legend=pie_chart_unified_legende)
    graphCountTicktStatusByDC = json.dumps(figCountTicktStatusByDC, cls=plotly.utils.PlotlyJSONEncoder)

    # TOP 10 USED NETWORKS BY DATACENTER
    colors=["#3D1766","#FF0032","#CD0404","#6F1AB6","#A6BB8D","#3C6255","#FFC6D3" , "#3C2A21" , "#ADA2FF" , "#CB1C8D"]
    labels_top_vlan_by_dc = query_top_used_networks_by_id_dc(id_datacenter)["name"]
    values_top_vlan_by_dc = query_top_used_networks_by_id_dc(id_datacenter)["servers"]
    figTopUsedVLANByDC = go.Figure(data=[go.Pie(labels=labels_top_vlan_by_dc, 
    hole =.2, marker=dict(colors=colors, line=dict(color='#FFFFFF', width=5)),
    values=values_top_vlan_by_dc, title = '')])
    figTopUsedVLANByDC.update_layout(margin=chart_margin_values)
    figTopUsedVLANByDC.update_layout(legend=pie_chart_unified_legende)
    graphTopUsedVLANByDC = json.dumps(figTopUsedVLANByDC, cls=plotly.utils.PlotlyJSONEncoder)

    # SERVER VITALITY CLASSIFICATION BY DATACENTER
    colors=["#B5D5C5","#B08BBB","#ECA869","#F5F5DC"]
    labels_vitality_by_dc = query_server_vitality_count_by_id_dc(id_datacenter)["vitality"]
    values_vitality_by_dc = query_server_vitality_count_by_id_dc(id_datacenter)["servers"]
    figTopUsedVLANByDC = go.Figure(data=[go.Pie(labels=labels_vitality_by_dc, 
    hole =.2, marker=dict(colors=colors, line=dict(color='#FFFFFF', width=5)),
    values=values_vitality_by_dc, title = '')])
    figTopUsedVLANByDC.update_layout(margin=chart_margin_values)
    figTopUsedVLANByDC.update_layout(legend=pie_chart_unified_legende)
    graphVitalityServerByDC = json.dumps(figTopUsedVLANByDC, cls=plotly.utils.PlotlyJSONEncoder)

    # DEVICE ROLE CLASSIFICATION COUNT BY DATACENTER
    colors=["#C69749","#735F32","#282A3A","#00005C","#3B185F","#C060A1","#F0CAA3"]
    labels_device_role_by_dc = query_device_role_count_by_id_dc(id_datacenter)["name"]
    values_device_role_by_dc = query_device_role_count_by_id_dc(id_datacenter)["device_count"]
    figTopUsedVLANByDC = go.Figure(data=[go.Pie(labels=labels_device_role_by_dc, 
    hole =.2, marker=dict(colors=colors, line=dict(color='#FFFFFF', width=5)),
    values=values_device_role_by_dc, title = '')])
    figTopUsedVLANByDC.update_layout(margin=chart_margin_values)
    figTopUsedVLANByDC.update_layout(legend=pie_chart_unified_legende)
    graphDeviceRoleUsedByDC = json.dumps(figTopUsedVLANByDC, cls=plotly.utils.PlotlyJSONEncoder)
        
     # VULNERABILITIES STATUS COUNT BY DATACENTER
    colors=["#2C74B3","#144272","#205295","#0A2647"]
    labels_vulnerabilities_status_by_dc = query_vulnerability_status_by_id_dc(id_datacenter)["status"]
    values_vulnerabilities_status_by_dc = query_vulnerability_status_by_id_dc(id_datacenter)["count_vlty"]
    figTopUsedVLANByDC = go.Figure(data=[go.Pie(labels=labels_vulnerabilities_status_by_dc, 
    hole =.2, marker=dict(colors=colors, line=dict(color='#FFFFFF', width=5)),
    values=values_vulnerabilities_status_by_dc, title = '')])
    figTopUsedVLANByDC.update_layout(margin=chart_margin_values)
    figTopUsedVLANByDC.update_layout(legend=pie_chart_unified_legende)
    graphVulnerabilitiesByDC = json.dumps(figTopUsedVLANByDC, cls=plotly.utils.PlotlyJSONEncoder)

    fig_server_type_by_dc = px.bar(query_server_type_count_by_id_dc(id_datacenter), 
                            y='servers', x='type', color='type',
                            labels = {'servers': 'SERVERS COUNT', 'type': 'IP TYPE'},
                            text = 'servers',                                
                            title="")
    fig_server_type_by_dc.update_layout(margin=chart_margin_values)
    fig_server_type_by_dc.update_layout(legend=pie_chart_unified_legende)
    graphBar_server_type_by_dc = json.dumps(fig_server_type_by_dc, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('admin/detailed_dashboard.html',    
                           datacenter_name = datacenter_name,
                           query_count_ip_dc=query_count_ip_dc,
                           query_count_rack_dc=query_count_rack_dc,                           
                           query_count_ticket_dc=query_count_ticket_dc,

                           count_ip_dc = 0 if count_ip_dc.empty else count_ip_dc.to_string(index = False, header = False),
                           count_rack_dc = 0 if count_rack_dc.empty else count_rack_dc.to_string(index = False, header = False),
                           count_ticket_dc = 0 if count_ticket_dc.empty else count_ticket_dc.to_string(index = False, header = False),
                           count_network_dc = 0 if count_network_dc.empty else count_network_dc.to_string(index = False, header = False),
                           count_vul_by_dc = 0 if count_vul_by_dc.empty else count_vul_by_dc.to_string(index = False, header = False),
                           count_u_dc = 0 if count_u_dc.empty else count_u_dc.to_string(index = False, header = False),
                           count_open_project = 0 if open_project.empty else open_project.to_string(index = False, header = False),
                           count_close_project =  0 if close_project.empty else close_project.to_string(index = False, header = False),

                           graphCountTicktStatusByDC = graphCountTicktStatusByDC,
                           graphTopUsedVLANByDC = graphTopUsedVLANByDC,
                           graphVitalityServerByDC = graphVitalityServerByDC,
                           graphDeviceRoleUsedByDC = graphDeviceRoleUsedByDC,
                           graphVulnerabilitiesByDC = graphVulnerabilitiesByDC,
                           graphBar_server_type_by_dc=graphBar_server_type_by_dc,
                           get_cloud_provider_details=get_cloud_provider_details,
                           datacenters=datacenters,
                           title="DATACENTER'S INFOS")