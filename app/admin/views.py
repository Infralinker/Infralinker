#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Author: Abdellah ALAOUI ISMAILI
#   
#  Project Name: InfraLinker
#  Project web Site: https://infralinker.net
"""
This view admin file containing the admin view functions for InfraLinker App, routes and the map to navigate in app.
"""

from flask import flash, redirect,abort, render_template, url_for, request, g, current_app,Flask
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime, time, date , timedelta
from .. import db, login_manager
from .forms import AdminRegistrationForm,DeviceRoleForm,ApplicationForm, AdminEditForm,ProjectDocumentsForm, DatacenterForm, ContractForm, ServerNetworkForm, PlatformRackForm, ImportCSVForm, RackForm, PlatformForm, NetworkForm, ServerForm, VulnerabilityForm, ProjectForm, DepartmentForm, SMTPConfigForm
from ..auth.forms import ResetPasswordForm, Add_Note_vunerability
from ..models import Admin,Tag, Supplier,Application ,Device_Role,ProjectDocuments, ChangeLog,Ticket,Contract, Platform, Vulnerability, Intervention, Project, Action, Contact, Datacenter,Rack, Network,Server, Select2MultipleField, Department, Emailling_config
from . import admin
from sqlalchemy import text, create_engine
from ..library.ip_calculator import get_subnet, get_total_hosts, get_ip_range, get_cidr, check_ip_in_network_by_id, check_expiration_date
from ..library.ssh_check import check_ssh_connexion
from ..library.querys import query_pname_u_position, query_details_rack
from ..library.emailling import change_log, send_email, get_cloud_provider_details
import io
from werkzeug.utils import secure_filename
import os
from sqlalchemy.sql import exists

def mydc_db_connexion():
    db_connection_str = current_app.config["SQLALCHEMY_DATABASE_URI"]
    db_connection = create_engine(db_connection_str)
    return db_connection

mydb = mydc_db_connexion()


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)
        
def check_permission_assets(control_stats, admin_stats):    
    """
    Prevent non-admin and non autorised user from accessing the pages
    """
    if not (control_stats or admin_stats):
        abort(403)

def get_UserName(id):
    first_name = db.session.query(Admin.firstname).filter(Admin.id == id).scalar()
    last_name = db.session.query(Admin.lastname).filter(Admin.id == id).scalar()
    return first_name, last_name

def get_tags_name():
    return Tag.query.all()

def get_applications_name():
    return Application.query.all()

#Get the FirstName and LastName of all Users
def get_members_name():
    return Admin.query.all()

def get_contacts_fullname():
    return Contact.query.all()

def check_if_member_of_project(id_user, member_liste):
    first_name = db.session.query(Admin.firstname).filter(Admin.id == id_user).scalar()
    last_name = db.session.query(Admin.lastname).filter(Admin.id == id_user).scalar()
    name = " ".join([first_name, last_name])
    if name in member_liste:
        return True

def get_tag_color(name):
    result = db.session.query(Tag.tag_color).filter(Tag.tag_name == name).scalar()
    return result

def get_ports_from_app_name(name_app):
    
    application_name = name_app.split('-')[0]
    application_version = name_app.split('-')[1]

    ports_list= db.session.query(Application.app_ports).filter(Application.app_name == application_name, Application.app_version == application_version).scalar()
    
    return ports_list

#CHECK THE DATE NOTUSED
import datetime
def date_comparator(end_date):
    result = datetime.date.today()<=end_date
    return result

########################################
### USERS AND ADMINS MANAGEMENT MODULE #
########################################

#ADD NEW USERS
@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
def new_admin():
    """
    Handle requests to the /register route
    Add an admin to the database through the registration form
    """
    check_admin()
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        admin = Admin(email=form.email.data,
                            firstname=form.firstname.data.capitalize(),
                            lastname=form.lastname.data.upper(),
                            phone=form.phone.data,
                            function = form.function.data.capitalize(),
                            department = form.department.data,
                            is_admin = form.is_admin.data,
                            is_manager = form.is_manager.data,
                            control_racks = form.control_racks.data,
                            control_platforms = form.control_platforms.data,
                            control_networks = form.control_networks.data,
                            control_servers = form.control_servers.data,
                            control_contracts = form.control_contracts.data,
                            control_applications = form.control_applications.data,
                            password=form.password.data)

        db.session.add(admin)
        db.session.commit()
        flash('You have successfully registered the new user!')
        
        change_log('User', 'New', admin.id, admin.firstname +" "+ admin.lastname )

        # redirect to the login page
        return redirect(url_for('home.admin_dashboard'))

    # load registration template
    return render_template('admin/users/register_new_admin.html', new_admin=new_admin,form=form, title='Register')

#SHOW LIST OF ALL USERS
@admin.route('/users', methods=['GET', 'POST'])
@login_required
def list_admins():
    """
    List all admins
    """
    check_admin()
    admins = Admin.query.all()
    return render_template('admin/users/admins.html',
                           admins=admins,
                           title="LISTE DES ADMINS")

def check_admin_dependencies(admin_id):
    dependent_models = [Project, Intervention, Ticket, Vulnerability]
    for model in dependent_models:
        if model.query.filter_by(admin_id=admin_id).first() is not None:
            return True
    return False

#DELETE USERS BY ADMIN
@admin.route('/users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_admin(id):
    """
    Delete a admin from the database
    """
    check_admin()
    if check_admin_dependencies(id) :        
        flash("Cannot delete this User with dependencies in Projects, Interventions, Tickets or Vulnerabilities. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_admins'))


    admin = Admin.query.get_or_404(id)
    db.session.delete(admin)
    db.session.commit()
    flash('User Deleted successfully.', 'danger')
    change_log('User', 'Delete', admin.id, admin.firstname +" "+ admin.lastname )
    return redirect(url_for('admin.list_admins'))


#EDIT USERS PROFIL BY ADMIN
@admin.route('/users/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_admin(id):
    """
    Edit a admin
    """
    check_admin()

    new_admin = False
    admin = Admin.query.get_or_404(id)
    form = AdminEditForm(obj=admin)
    form.origin_email.data = admin.email
    form.origin_phone.data = admin.phone

    if form.validate_on_submit():

        admin.firstname = form.firstname.data.capitalize()
        admin.lastname = form.lastname.data.upper()
        admin.email = form.email.data
        admin.phone = form.phone.data
        admin.function = form.function.data.capitalize()
        admin.department = form.department.data
        admin.is_admin = form.is_admin.data
        admin.is_manager = form.is_manager.data
        admin.control_racks = form.control_racks.data
        admin.control_platforms = form.control_platforms.data
        admin.control_networks = form.control_networks.data
        admin.control_servers = form.control_servers.data
        admin.control_contracts = form.control_contracts.data
        admin.control_applications = form.control_applications.data
        admin.change_password = form.change_password.data

        db.session.commit()
        flash('Edited User Saved successfully!')
        change_log('User', 'Edit', admin.id, admin.firstname +" "+ admin.lastname )

        # redirect to the admins page
        return redirect(url_for('admin.list_admins'))

    form.firstname.data = admin.firstname
    form.lastname.data = admin.lastname
    form.email.data = admin.email
    form.phone.data = admin.phone
    form.function.data = admin.function
    form.department.data = admin.department
    form.is_admin.data = admin.is_admin
    form.is_manager.data = admin.is_manager
    form.control_platforms = admin.control_racks
    form.control_racks = admin.control_platforms
    form.control_networks = admin.control_networks
    form.control_servers = admin.control_servers
    form.control_contracts = admin.control_contracts
    form.control_applications = admin.control_applications
    form.change_password.data = admin.change_password

    return render_template('admin/users/register_new_admin.html', action="Edit Users",
                           new_admin=new_admin, form=form,
                           admin=admin, title="Edit Admin")

#THIS FUNCTION IS TO RESET PASSWORD BY ADMIN FOR USERS
@admin.route('/change_password/to_user_<int:id>', methods=['GET','POST'])
@login_required
def admin_password_resetter(id):

    check_admin()

    user_change = Admin.query.get_or_404(id)
    form = ResetPasswordForm(obj=user_change)

    if form.validate_on_submit():
        user_change.password = form.new_password.data
        user_change.change_password = True
        db.session.add(user_change)
        db.session.commit()
        flash('Password changed successfully!')        

        return redirect(url_for('home.admin_dashboard'))

    return render_template('admin/users/change_password.html',
                form=form, title=('Reset Password!'))

#################################################
### DEPARTMENTS MANAGEMENT MODULE ONLY FOR ADMINISTRATOR  ##
#################################################

@admin.route('/departments', methods=['GET', 'POST'])

@login_required
def list_departments():
    """
    List all departments
    """
    # check_admin()

    departments = Department.query.all()

    return render_template('admin/departments/departments.html',
                           departments=departments, title="Departments")

@admin.route('/departments/add', methods=['GET', 'POST'])
@login_required
def new_department():
    """
    Add a department to the database
    """
    check_admin()

    new_department = True

    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(name=form.name.data.upper(),
                                description=form.description.data)
        try:
            # add department to the database
            db.session.add(department)
            db.session.commit()
            change_log('Department', 'New' , department.id, department.name)
            flash('You have successfully added a new department.')
        except:
            # in case department name already exists
            flash('Error: department name already exists.')

        # redirect to departments page
        return redirect(url_for('admin.list_departments'))

    # load department template
    return render_template('admin/departments/department.html', action="Add",
                           new_department=new_department, form=form,
                           title="Add Department")

@admin.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    """
    Edit a department
    """
    check_admin()

    new_department = False

    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.name = form.name.data.upper()
        department.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the department.')
        change_log('Department', 'Edit', department.id, department.name)

        
        return redirect(url_for('admin.list_departments'))

    form.description.data = department.description
    form.name.data = department.name
    return render_template('admin/departments/department.html', action="Edit",
                           new_department=new_department, form=form,
                           department=department, title="Edit Department")


# Function to check if there are dependencies for Multible Model
def check_department_dependencies(department_id):
    dependent_models = [Admin, Server]
    for model in dependent_models:
        if model.query.filter_by(department_id=department_id).first() is not None:
            return True
    return False

@admin.route('/departments/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    """
    Delete a department from the database
    """
    check_admin()
    if check_department_dependencies(id) :        
        flash("Cannot delete this Department with dependencies in User or Server/IP. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_departments'))


    department = Department.query.get_or_404(id)
    change_log('Department', 'Delete', department.id, department.name)
    db.session.delete(department)
    db.session.commit()
    
    flash('You have successfully deleted the department.')

    
    return redirect(url_for('admin.list_departments'))

    
###########################################################
### DATACENTER MANAGEMENT MODULE ONLY FOR ADMINISTRATOR #
###########################################################
@admin.route('/datacenters/list', methods=['GET', 'POST'])

@login_required
def list_datacenters():
    """
    List all datacenters
    """
    datacenters = Datacenter.query.all()
    return render_template('admin/datacenters/datacenters.html',
                           datacenters=datacenters, get_cloud_provider_details=get_cloud_provider_details,
                           title="DATA CENTERS LIST")

@admin.route('/datacenters/new', methods=['GET', 'POST'])
@login_required
def new_datacenter():
    """
    Handle requests to the datacenter new route
    """
    check_admin()
    form = DatacenterForm()
    if form.validate_on_submit():
        datacenter = Datacenter(dc_name=form.dc_name.data.upper(),
                            dc_type=form.dc_type.data,
                            dc_address=form.dc_address.data,
                            dc_city=form.dc_city.data.upper(),
                            dc_country=form.dc_country.data.upper(),
                            dc_phone = form.dc_phone.data)

        db.session.add(datacenter)
        db.session.commit()
        flash('You have successfully add new DataCenter.')

        # redirect to the login page
        return redirect(url_for('admin.list_datacenters'))

    # load registration template
    return render_template('admin/datacenters/datacenter.html', new_datacenter=new_datacenter,form=form, title='NEW DATACENTER')

# Check Datacenter dependencies
def check_datacenter_dependencies(datacenter_id):
    # List of models that may have dependencies on the Supplier
    dependent_models = [Rack, Network]

    # Check if the contract is referenced in any of the models
    for model in dependent_models:
        if model.query.filter_by(datacenter_id=datacenter_id).first() is not None:
            return True

    return False

@admin.route('/datacenters/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_datacenter(id):
    """
    Delete a data center from the database
    """
    check_admin()

    if check_datacenter_dependencies(id) :        
        flash("Cannot delete this DataCenter with dependencies in Racks or Networks. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_datacenters'))

    datacenter = Datacenter.query.get_or_404(id)
    db.session.delete(datacenter)
    db.session.commit()
    flash('DataCenter Deleted successfully.', 'danger')

    return redirect(url_for('admin.list_datacenters'))
    

@admin.route('/datacenters/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_datacenter(id):
    """
    Edit a DataCenter
    """
    check_admin()
    new_datacenter = False
    datacenter = Datacenter.query.get_or_404(id)
    form = DatacenterForm(obj=datacenter)
    form.origin_dc_name.data = datacenter.dc_name

    if form.validate_on_submit():
        datacenter.dc_name = form.dc_name.data
        datacenter.dc_type = form.dc_type.data
        datacenter.dc_address = form.dc_address.data
        datacenter.dc_city = form.dc_city.data
        datacenter.dc_country = form.dc_country.data
        datacenter.dc_phone = form.dc_phone.data

        db.session.commit()
        flash('DataCenter Edited successfully.')

        # redirect to the admins page
        return redirect(url_for('admin.list_datacenters'))

    form.dc_name.data = datacenter.dc_name
    form.dc_type.data = datacenter.dc_type
    form.dc_address.data = datacenter.dc_address
    form.dc_city.data = datacenter.dc_city
    form.dc_country.data = datacenter.dc_country
    form.dc_phone.data = datacenter.dc_phone

    return render_template('admin/datacenters/datacenter.html', action="Edit",
                           new_datacenter=new_datacenter, form=form,
                           datacenter=datacenter, title="Edit DataCenter")


########################################
### RACK MANAGEMENT MODULE ####
########################################
@admin.route('/racks/list', methods=['GET', 'POST'])
@login_required
def list_racks():
    """
    List all RACKS
    """
    racks = Rack.query.all()
    return render_template('admin/racks/racks.html',
                           racks=racks,
                           get_tag_color=get_tag_color,
                           get_cloud_provider_details=get_cloud_provider_details,
                           title="RACKS LIST")

@admin.route('/racks/new', methods=['GET', 'POST'])
@login_required
def new_rack():
    """
    Handle requests to the rack new route
    """
    check_permission_assets(current_user.control_racks, current_user.is_admin)
    
    form = RackForm()
    if form.validate_on_submit():
        rack = Rack(r_name=form.r_name.data.upper(),
                            ru_hight=form.ru_hight.data,
                            r_position=form.r_position.data,
                            datacenter=form.datacenter.data,
                            installation_date=form.installation_date.data,
                            tags = form.tags.data,
                            add_by = current_user.id,
                            add_date = datetime.datetime.now(),
                            r_notes=form.r_notes.data.capitalize())

        db.session.add(rack)
        db.session.commit()
        flash('You have successfully add new rack.')
        change_log('Rack', 'New', rack.id, rack.r_name)

        # redirect to the login page
        return redirect(url_for('admin.list_racks'))

    # load registration template
    return render_template('admin/racks/rack.html', new_rack=new_rack,form=form, get_tags_name=get_tags_name, title='NEW RACK')


def check_rack_dependencies(rack_id):    
    return Platform.query.filter_by(rack_id=rack_id).first() is not None

@admin.route('/racks/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_rack(id):
    """
    Delete a Rack from the database
    """
    if check_rack_dependencies(id) :        
        flash("Cannot delete this rack with dependencies in Device. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_racks'))

    check_permission_assets(current_user.control_racks, current_user.is_admin)
    rack = Rack.query.get_or_404(id)
    db.session.delete(rack)
    db.session.commit()
    flash('Rack Deleted successfully.', 'danger')
    change_log('Rack', 'Delete', rack.id, rack.r_name)

    return redirect(url_for('admin.list_racks'))
    

@admin.route('/racks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_rack(id):
    """
    Edit a Rack
    """
    check_permission_assets(current_user.control_racks, current_user.is_admin)
    
    new_rack = False
    rack = Rack.query.get_or_404(id)
    form = RackForm(obj=rack)
    form.origin_rack.data = rack.r_name

    if form.validate_on_submit():
        rack.r_name = form.r_name.data.upper()
        rack.ru_hight = form.ru_hight.data
        rack.r_position = form.r_position.data
        rack.datacenter = form.datacenter.data
        rack.tags = form.tags.data
        rack.installation_date = form.installation_date.data
        rack.r_notes = form.r_notes.data.capitalize()

        db.session.commit()
        flash('Edited Rack Saved successfully!')
        change_log('Rack', 'Edit', rack.id, rack.r_name)

        # redirect to the admins page
        return redirect(url_for('admin.list_racks'))

    form.r_name.data = rack.r_name
    form.ru_hight.data = rack.ru_hight
    form.r_position.data = rack.r_position
    form.datacenter.data = rack.datacenter
    form.tags.data = rack.tags
    form.installation_date.data = rack.installation_date
    form.r_notes.data = rack.r_notes

    return render_template('admin/racks/rack.html', action="Edit",
                           new_rack=new_rack, form=form,
                           get_tags_name=get_tags_name,
                           rack=rack, title="Edit Rack")

######################################
###PLATEFORMES MANAGEMENT MODULE #####
######################################
def units_calculator(position):
     start, end = position.split('-')
     start = int(start)
     end = int(end)
     result = end-start+1
     return result

@admin.route('/platform/new/', methods=['GET', 'POST'])
@login_required
def new_platform():
    """
    Add an platform to the database through the project form
    """
    check_permission_assets(current_user.control_platforms, current_user.is_admin)
    form = PlatformForm()
    if form.validate_on_submit():
        platform = Platform(
        platform_name = form.platform_name.data.upper(),
        serial_number = form.serial_number.data.upper(),
        device_role = form.device_role.data,
        supplier = form.supplier.data,
        rack = form.rack.data,
        u_position = form.u_position.data, #"0-0" if form.platform_type.data=="SOFTWARE" else form.u_position.data,
        power_supply =  0 if  form.power_supply.data=='' else form.power_supply.data,
        production_date = form.production_date.data,
        end_warranty_date = form.end_warranty_date.data,
        u_hight = 0 if form.u_position.data=='' else units_calculator(form.u_position.data),
        network_identity = form.network_identity.data,
        contract = form.contract.data,
        tags = form.tags.data,
        add_by = current_user.id,
        add_date = datetime.datetime.now(),
        notes = form.notes.data.capitalize())

        try:
            # add platform to the database
            db.session.add(platform)
            db.session.commit()
            flash('You have successfully added a new Device !')
            change_log('Platform/Device', 'New', platform.id, platform.platform_name)
        
        except Exception as e:
            flash('Failed to Save : '+ str(e), 'danger')

        # redirect to platforms page
        return redirect(url_for('admin.list_platforms'))

    # load department template
    return render_template('admin/platforms/platform.html',new_platform=new_platform ,
                        platform="Add", form=form,
                        get_tags_name=get_tags_name,
                           title="ADD NEW DEVICE")

@admin.route('/platform/new/<int:id_rack>', methods=['GET', 'POST'])
@login_required
def new_platform_from_rack(id_rack):
    """
    Add an platform to the database through the rack over view
    """
    rack = Rack.query.get(id_rack)

    if not rack:
        flash('Error: invalid rack')
        abort(404)

    check_permission_assets(current_user.control_platforms, current_user.is_admin)
    form = PlatformRackForm()
    if form.validate_on_submit():
        platform = Platform(
        platform_name = form.platform_name.data.upper(),
        serial_number = form.serial_number.data.upper(),
        device_role = form.device_role.data,
        supplier = form.supplier.data,
        rack = rack,
        u_position = form.u_position.data,
        power_supply =  0 if form.power_supply.data=='' else form.power_supply.data,
        production_date = form.production_date.data,
        end_warranty_date = form.end_warranty_date.data,
        u_hight = 0 if form.u_position.data=='' else units_calculator(form.u_position.data),
        network_identity = form.network_identity.data,
        contract = form.contract.data,
        tags = form.tags.data,
        add_by = current_user.id,
        add_date = datetime.datetime.now(),
        notes = form.notes.data.capitalize()
        )
        try:
            # add platform to the database
            db.session.add(platform)
            db.session.commit()
            flash('You have successfully added a new Device.')
            change_log('Platform/Device', 'New', platform.id, platform.platform_name)
        
        except Exception as e:
            flash('Failed to Save : '+ str(e), 'danger')

        # redirect to platforms page
        return redirect(url_for('admin.rack_overview', id=id_rack))

    # load department template
    return render_template('admin/platforms/platform.html',new_platform=new_platform ,
                        platform="Add", form=form,
                        get_tags_name=get_tags_name,
                           title="ADD NEW PLATFORM")

@admin.route('/platforms/list', methods=['GET'])
@login_required
def list_platforms():
    """()
    List all platforms
    """
    platforms = Platform.query.all()
    return render_template('admin/platforms/platforms.html', date_comparator=date_comparator, check_expiration_date=check_expiration_date,
    platforms=platforms, title="LISTE ALL PLATFORMS")

# LIST ALL PLATFORM FROM RACK
import pandas as pd
@admin.route('/platforms/rack/<int:id>', methods=['GET'])
@login_required
def list_platform_from_rack(id):
    """()
    List all platforms from selected rack
    """
    platforms = Platform.query.filter_by(rack_id=id).all()

    return render_template('admin/platforms/platforms.html', date_comparator=date_comparator, check_expiration_date=check_expiration_date,get_tag_color=get_tag_color,
    platforms=platforms, title="LISTE ALL PLATFORMS FRM SELECTED RACK")

@admin.route('/platform/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_platform(id):
    """
    Edit a platform
    """
    check_permission_assets(current_user.control_platforms, current_user.is_admin)
    
    new_platform = False

    platform = Platform.query.get_or_404(id)
    form = PlatformForm(obj=platform)
    if form.validate_on_submit():

        platform.platform_name = form.platform_name.data.upper()
        platform.serial_number = form.serial_number.data.upper()
        platform.supplier = form.supplier.data
        platform.rack = form.rack.data # None if form.platform_type.data=="SOFTWARE" else form.rack.data
        platform.u_position = form.u_position.data #"0-0" if form.platform_type.data=="SOFTWARE" else form.u_position.data
        platform.device_role = form.device_role.data
        platform.production_date = form.production_date.data
        platform.u_hight = 0 if form.u_position.data=='' else units_calculator(form.u_position.data) #units_calculator(form.u_position.data)
        platform.power_supply = 0 if form.power_supply.data=='' else form.power_supply.data #0 if form.platform_type.data=="SOFTWARE" or form.power_supply.data=='' else form.power_supply.data
        platform.end_warranty_date = form.end_warranty_date.data
        platform.network_identity = form.network_identity.data
        platform.contract = form.contract.data
        platform.tags = form.tags.data
        platform.notes = form.notes.data.capitalize()

        db.session.commit()
        flash('Edited Device Saved successfully!')
        change_log('Platform/Device', 'Edit', platform.id, platform.platform_name)

        return redirect(url_for('admin.rack_overview', id=form.rack.data.id))

    form.platform_name.data = platform.platform_name
    form.serial_number.data = platform.serial_number
    form.supplier.data = platform.supplier
    form.rack.data = platform.rack
    form.u_hight.data = platform.u_hight
    form.u_position.data = platform.u_position
    form.device_role.data = platform.device_role
    form.production_date.data = platform.production_date
    form.contract.data = platform.contract
    form.tags.data = platform.tags
    form.power_supply.data = platform.power_supply
    form.end_warranty_date.data = platform.end_warranty_date
    form.network_identity.data = platform.network_identity
    form.notes.data = platform.notes

    return render_template('admin/platforms/platform.html',
                            get_tags_name=get_tags_name,
                           new_platform=new_platform, form=form,
                           platform=platform, title="Edit platform")

# Function to check if there are dependencies for Multible Model
def check_platform_dependencies(platform_id):
    dependent_models = [Ticket, Server]
    for model in dependent_models:
        if model.query.filter_by(platform_id=platform_id).first() is not None:
            return True
    return False

@admin.route('/platform/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_platform(id):
    """
    Delete a platform from the database
    """
    check_permission_assets(current_user.control_platforms, current_user.is_admin)

    if check_platform_dependencies(id) :        
        flash("Cannot delete this Device with dependencies in Ticket or Server/IP. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_platforms'))

    platform = Platform.query.get_or_404(id)
    db.session.delete(platform)
    db.session.commit()
    flash('Device Deleted successfully.', 'danger')
    change_log('Platform/Device', 'Delete', platform.id, platform.platform_name)

    
    return redirect(url_for('admin.list_platforms'))

    
@admin.route('/details/platform/<int:id>', methods=['GET'])
@login_required
def platform_details(id):
    """
    Show platform Details
    """
    platform = Platform.query.get_or_404(id)
    tickets = Ticket.query.filter_by(platform_id = id).all()
    return render_template('admin/platforms/platform_details.html', 
    get_tag_color=get_tag_color, platform=platform, get_UserName=get_UserName, tickets=tickets,
    check_expiration_date=check_expiration_date,
    title="SHOW DEVICE DETAILS")
############################################
####  RACKS OVERVIEWS AND DETAILS ##########
############################################
from collections import namedtuple
import pandas as pd

@admin.route('/platforms/rack_overview/<int:id>', methods=['GET'])

@login_required
def rack_overview(id):
    """
    Overview of  all platforms from selected rack
    """
    platforms = Platform.query.filter_by(rack_id=id).all()

    COLUMNS = ['name', 'start', 'end', 'units']
    
    Section = namedtuple('Section', COLUMNS)
    t_units = db.session.query(Rack.ru_hight).filter(Rack.id == id).scalar()
    def parse_rows(df_query, limit):
        sections = []
        
        for index, row, in df_query.iterrows():
            name = row['platform_name']
            start, end = row['u_position'].strip().split('-')
            start, end, = int(start), int(end)
            assert 0 < start and start <= end <= limit, 'Incorrect declaration'
            sections.append(Section(name, start, end, end - start + 1))
            sort_sections = sorted(sections, key=lambda x: x[1], reverse=True)

        last = 0
        rows = []
        try:
            for s in sorted(sort_sections, key=lambda x: x.start):
                assert s.start - last > 0, 'Double affectation : There is a conflict in the units position in this rack, Please re-Check the position to visualize all devices in this Rack !!!!'
                units = s.start - last - 1
                if units > 0: rows.append(Section('empty', last + 1, s.start - 1, units))
                rows.append(s)
                last = s.end

        except Exception as e:
            flash('WARNING !!! \n '+ str(e), 'danger')

        if limit - last:
            rows.append(Section('empty', last + 1, limit, limit - last))

        return rows
    
    limit = t_units
    query_is_empty = True
    rows = []
    query_rack_infos = query_details_rack(id)
    
    pd.set_option('display.max_colwidth', -1)

    if not query_pname_u_position(id).empty:
        query_is_empty = False
        df = pd.DataFrame(query_pname_u_position(id), columns = ['platform_name', 'u_position']) 
        rows = parse_rows(df, limit)
    else:
        query_is_empty = True
        

    return render_template('admin/racks/rack_overview.html', 
                        rows=rows,query_rack_infos=query_rack_infos, 
                        query_is_empty=query_is_empty,id=id, 
                        check_expiration_date=check_expiration_date,
                        get_cloud_provider_details=get_cloud_provider_details,
                        get_tag_color=get_tag_color,platforms=platforms, title="LISTE ALL PLATFORMS FRM SELECTED RACK")

##########################################
####        DEVICE ROLES         #########
##########################################
@admin.route('/deviceroles', methods=['GET', 'POST'])
@login_required
def devices_role_list():
    """
    List all device roles
    """
    device_roles = Device_Role.query.all()
    return render_template('admin/platforms/roles/roles.html',
                           device_roles=device_roles, title="DEVICE ROLES LISTE")

@admin.route('/devicerole/new', methods=['GET', 'POST'])
@login_required
def new_device_role():
    """
    Add new device role to the database
    """
    new_device_role = True
    form = DeviceRoleForm()
    if form.validate_on_submit():
        device_role = Device_Role(
            name=form.name.data.upper(),
            description = form.description.data,
            device_color = form.device_color.data,
            )
        try:
            db.session.add(device_role)
            db.session.commit()
            flash('You have successfully added a new Role.')
            change_log('DeviceRole', 'New', device_role.id, device_role.name)
        except:
            flash('Error: Device role already exists.')

        return redirect(url_for('admin.devices_role_list'))
    return render_template('admin/platforms/roles/role.html', action="Add",
                           new_device_role=new_device_role, form=form,
                           title="ADD NEW DEVICE ROLE")

@admin.route('/devicerole/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_device_role(id):
    """
    Edit a device role
    """
    check_permission_assets(current_user.control_platforms, current_user.is_admin)

    new_device_role = False
    device_role = Device_Role.query.get_or_404(id)
    form = DeviceRoleForm(obj=device_role)
    if form.validate_on_submit():

        device_role.name = form.name.data.upper()
        device_role.description = form.description.data
        device_role.device_color = form.device_color.data

        db.session.commit()
        flash('Edited Device role Saved successfully!')
        change_log('DeviceRole', 'Edit', device_role.id, device_role.name)
        return redirect(url_for('admin.devices_role_list'))

    form.name.data = device_role.name
    form.description.data = device_role.description
    form.device_color.data = device_role.device_color

    return render_template('admin/platforms/roles/role.html', action="Edit",
                           new_device_role=new_device_role, form=form,
                           device_role=device_role, title="EDIT DEVICE ROLE")


def check_device_role_dependencies(device_role_id):    
    return Platform.query.filter_by(device_role_id=device_role_id).first() is not None

@admin.route('/tag/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_device_role(id):
    """
    Delete a Device Role from the database
    """
    
    check_permission_assets(current_user.control_platforms, current_user.is_admin)

    if check_device_role_dependencies(id) :        
        flash("Cannot delete this Device Role with dependencies in Device. Please check before Deleting.", 'error')
        return redirect(url_for('admin.devices_role_list'))


    device_role = Device_Role.query.get_or_404(id)
    db.session.delete(device_role)
    db.session.commit()
    flash('Device role Deleted successfully.', 'danger')
    change_log('DeviceRole', 'Delete', device_role.id, device_role.name)

    
    return redirect(url_for('admin.devices_role_list'))

#######################################
### NETWORKS MANAGEMENT MODULE ########
#######################################
@admin.route('/network/new', methods=['GET', 'POST'])
@login_required
def new_network():
    """
    Add an network to the database
    """
    check_permission_assets(current_user.control_networks, current_user.is_admin)
    
    form = NetworkForm()
    if form.validate_on_submit():
        network = Network(
        net_name = form.net_name.data.upper(),
        datacenter = form.datacenter.data,
        tag = form.tag.data,
        mask = form.mask.data,
        gatway = form.gatway.data,
        tags = form.tags.data,
        add_by = current_user.id,
        add_date = datetime.datetime.now(),
        net_notes = form.net_notes.data.capitalize())

        try:
            # add platform to the database
            db.session.add(network)
            db.session.commit()
            flash('You have successfully added a new network.')
            change_log('Network', 'New', network.id, network.net_name)

        except:
            flash('Error: network name already exists.')
        
        # redirect to platforms page
        return redirect(url_for('admin.list_networks'))

    # load department template
    return render_template('admin/networks/network.html',new_network=new_network ,
    network="Add", form=form,
    get_tags_name=get_tags_name,
                           title="ADD NEW NETWORK")

@admin.route('/networks/list', methods=['GET'])

@login_required
def list_networks():
    """
    List all networks
    """
    networks = Network.query.all()

    return render_template('admin/networks/networks.html', networks=networks,
    get_subnet=get_subnet,
    get_total_hosts = get_total_hosts,
    get_ip_range = get_ip_range,
    get_cidr = get_cidr,
    get_tag_color=get_tag_color,
    get_cloud_provider_details=get_cloud_provider_details,
    title="LISTE ALL NETWORKS")

@admin.route('/network/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_network(id):
    """
    Edit a network
    """
    check_permission_assets(current_user.control_networks, current_user.is_admin)
    new_network = False

    network = Network.query.get_or_404(id)
    form = NetworkForm(obj=network)
    form.origin_tag.data = network.tag
    form.origin_gatway.data = network.gatway

    if form.validate_on_submit():
        network.net_name = form.net_name.data.upper()
        network.tag = form.tag.data
        network.mask = form.mask.data
        network.datacenter = form.datacenter.data
        network.tags = form.tags.data
        network.gatway = form.gatway.data
        network.net_notes = form.net_notes.data.capitalize()

        db.session.commit()
        flash('Edited Network Saved successfully!')
        change_log('Network', 'Edit', network.id, network.net_name)

        
        return redirect(url_for('admin.list_networks'))

    form.net_name.data = network.net_name
    form.tag.data = network.tag
    form.mask.data = network.mask
    form.datacenter.data = network.datacenter
    form.tags.data = network.tags
    form.gatway.data = network.gatway
    form.net_notes.data = network.net_notes

    return render_template('admin/networks/network.html',
                           new_network=new_network, form=form,      
                           get_tags_name=get_tags_name,                     
                           network=network, title="Edit Network")

def check_network_dependencies(network_id):    
    return Server.query.filter_by(network_id=network_id).first() is not None

@admin.route('/network/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_network(id):
    """
    Delete a network from the database
    """
    check_permission_assets(current_user.control_networks, current_user.is_admin)

    if check_network_dependencies(id) :        
        flash("Cannot delete this network with dependencies in Server/IP. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_networks'))

    network = Network.query.get_or_404(id)
    db.session.delete(network)
    db.session.commit()
    flash('Network Deleted successfully.', 'danger')
    change_log('Network', 'Delete', network.id, network.net_name)

    
    return redirect(url_for('admin.list_networks'))

#######################################
###SERVERS MANAGEMENT MODULE #####
#######################################

@admin.route('/server/new', methods=['GET', 'POST'])
@login_required
def new_server():
    """
    Add an server to the database
    """
    check_permission_assets(current_user.control_servers, current_user.is_admin)
    form = ServerForm()
    if form.validate_on_submit():
        server = Server(
        server_name = form.server_name.data,
        operating_system = form.operating_system.data,
        os_version = form.os_version.data,
        type = form.type.data,
        ip_address = form.ip_address.data,
        network = form.network.data,
        project = form.project.data,
        platform = form.platform.data,
        department = form.department.data,
        add_by = current_user.id,
        vitality_classification = form.vitality_classification.data,
        notes = form.notes.data,
        tags = form.tags.data,
        add_date = datetime.datetime.now(),
        applications_list = form.applications_list.data)

        try:
            db.session.add(server)
            db.session.commit()
            flash('You have successfully added a new IP / Server.')
            change_log('Server/IP', 'New', server.id, server.server_name)

        except Exception as e:
            flash('Failed to Save to database: '+ str(e), 'danger')

        return redirect(url_for('admin.list_servers'))
    return render_template('admin/servers/server.html',new_server=new_server, get_tags_name=get_tags_name , get_applications_name=get_applications_name, server="Add", form=form,
                           title="ADD NEW SERVER")

@admin.route('/server/new/network/<int:id_network>', methods=['GET', 'POST'])
@login_required
def new_server_from_network(id_network):
    """
    Add an server to the database
    """
    check_permission_assets(current_user.control_servers, current_user.is_admin)

    network = Network.query.get(id_network)
    add_server_from_network = True
    
    if not network:
        flash('Error: invalid network ')
        abort(404)

    form = ServerNetworkForm()
    if form.validate_on_submit():
        server = Server(
        server_name = form.server_name.data,
        operating_system = form.operating_system.data,
        os_version = form.os_version.data,
        type = form.type.data,
        ip_address = form.ip_address.data,
        network = network,
        project = form.project.data,
        platform = form.platform.data,
        department = form.department.data,
        add_by = current_user.id,
        vitality_classification = form.vitality_classification.data,
        notes = form.notes.data,
        tags = form.tags.data,
        add_date = datetime.datetime.now(),
        applications_list = form.applications_list.data)

        if not check_ip_in_network_by_id(network.id, form.ip_address.data):
            flash('Please Check, IP Address is not in range of the selected Network','error'),
            
        else:   
            try:
                db.session.add(server)
                db.session.commit()
                flash('You have successfully added a new IP / Server.')
                change_log('Server/IP', 'New', server.id, server.server_name)

            except Exception as e:
                flash('Failed to Save to database: '+ str(e), 'danger')

            return redirect(url_for('admin.list_servers'))
    return render_template('admin/servers/server.html',new_server=new_server, get_tags_name=get_tags_name ,network=network, add_server_from_network=add_server_from_network, get_applications_name=get_applications_name, server="Add", form=form, get_subnet=get_subnet, get_cidr = get_cidr,
                           title="ADD NEW SERVER")

@admin.route('/servers/list', methods=['GET'])

@login_required
def list_servers():
    """
    List all servers
    """
    servers = Server.query.all()

    return render_template('admin/servers/servers.html', servers=servers, 
    check_ssh_connexion=check_ssh_connexion,
    get_tag_color=get_tag_color,
    title="LISTE ALL SERVERS")

@admin.route('/servers/network/<int:id>', methods=['GET'])

@login_required
def list_ip_from_network(id):
    """
    List all servers from selected network
    """
    servers = Server.query.filter_by(network_id=id).all()
    
    return render_template('admin/servers/servers.html', servers=servers,get_tag_color=get_tag_color, check_ssh_connexion=check_ssh_connexion ,title="LISTE ALL SERVERS FROM NETWORK")

@admin.route('/server/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_server(id):
    """
    Edit a server
    """
    check_permission_assets(current_user.control_servers, current_user.is_admin)
    new_server = False
    server = Server.query.get_or_404(id)
    form = ServerForm(obj=server)
    form.origin_ip.data = server.ip_address

    if form.validate_on_submit():

        server.server_name = form.server_name.data
        server.operating_system = form.operating_system.data
        server.os_version = form.os_version.data
        server.type = form.type.data
        server.ip_address = form.ip_address.data
        server.vitality_classification = form.vitality_classification.data
        server.notes = form.notes.data
        server.tags = form.tags.data
        server.network = form.network.data
        server.project = form.project.data
        server.platform = form.platform.data
        server.department = form.department.data
        server.applications_list = form.applications_list.data

        try:
            db.session.add(server)
            db.session.commit()
            flash('Edited IP Saved successfully!')
            change_log('Server/IP', 'Edit', server.id, server.server_name)

        except Exception as e:
            flash('Failed to Save to database: '+ str(e), 'danger')

        return redirect(url_for('admin.list_servers'))

    form.server_name.data = server.server_name
    form.operating_system.data = server.operating_system
    form.os_version.data = server.os_version
    form.type.data = server.type
    form.ip_address.data = server.ip_address
    form.vitality_classification.data = server.vitality_classification
    form.network.data = server.network
    form.platform.data = server.platform
    form.department.data = server.department
    form.notes.data = server.notes
    form.tags.data = server.tags
    form.applications_list.data =server.applications_list

    return render_template('admin/servers/server.html',
                           new_server=new_server, form=form,
                           get_tags_name=get_tags_name,
                           get_applications_name=get_applications_name,
                           server=server, title="Edit Server")

@admin.route('/server/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_server(id):
    """
    Delete a server from the database
    """
    check_permission_assets(current_user.control_servers, current_user.is_admin)
    server = Server.query.get_or_404(id)
    db.session.delete(server)
    db.session.commit()
    flash('IP Deleted successfully.', 'danger')
    change_log('Server/IP', 'Delete', server.id, server.server_name)

    return redirect(url_for('admin.list_servers'))

@admin.route('/details/server/<int:id>', methods=['GET'])
@login_required
def server_details(id):
    """
    Show Server Details
    """
    server = Server.query.get_or_404(id)
    return render_template('admin/servers/server_details.html',get_ports_from_app_name=get_ports_from_app_name,get_cloud_provider_details=get_cloud_provider_details, get_tag_color=get_tag_color, server=server, get_UserName=get_UserName,
    title="SHOW SERVER DETAILS")

##########################################
###VULNERABILITIES MANAGEMENT MODULE #####
##########################################
@admin.route('/vulnerability/new', methods=['GET', 'POST'])
@login_required
def new_vulnerability():
    """
    Add an vulnerability to the database
    """
    emailling_details = Emailling_config.query.get_or_404(1)
    form = VulnerabilityForm()
    if form.validate_on_submit():
        vulnerability = Vulnerability(
        title_vulnerability = form.title_vulnerability.data,
        date_vulnerability = form.date_vulnerability.data,
        cvs_code = form.cvs_code.data.upper(),
        severity = form.severity.data,
        risk = form.risk.data,
        impact = form.impact.data,
        ticket = form.ticket.data,
        admin = form.admin.data,
        add_by = current_user.id,
        add_date = datetime.datetime.now(),
        recommanded_solution = form.recommanded_solution.data.capitalize())

        try:
            db.session.add(vulnerability)
            db.session.commit()
            flash('You have successfully added a new vulnerability.')
            change_log('Vulnerability', 'New', vulnerability.id, vulnerability.title_vulnerability)

            # SEND EMAIL TO GROUPE FOR NEW VULNERABILITY
            emails_group = emailling_details.egroup_vulnerability

            if emails_group :

                recipients = [email.strip() for email in emails_group.strip('()').split(',')]
                send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
                subject = (""" [INFRALINKER] - NEW VULNERABILITY HAVE BEEN ADDED. """)
                html_template = render_template('email/email-vulnerability.html', vulnerability=vulnerability, send_time=send_time)

                try:
                    send_email(recipients, subject, html_template)

                except Exception as e:
                    flash(f"Error sending email: {e}")
            else :
                pass

        except Exception as e:
            flash('Failed to Save to DataBase: '+ str(e), 'danger')

        # redirect to platforms page
        return redirect(url_for('admin.list_vulnerabilities'))

    # load department template
    return render_template('admin/vulnerabilities/vulnerability.html',new_vulnerability=new_vulnerability ,vulnerability="Add", form=form,
                           title="ADD NEW VULNERABILITY")

@admin.route('/vulnerabilities/list', methods=['GET'])

@login_required
def list_vulnerabilities():
    """
    List all vulnerabilities
    """
    vulnerabilities = Vulnerability.query.order_by(Vulnerability.date_vulnerability.desc()).all()

    return render_template('admin/vulnerabilities/vulnerabilities.html', vulnerabilities=vulnerabilities, title="LISTE ALL VULNERABILITIES")

@admin.route('/vulnerability/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vulnerability(id):
    """
    Edit a vulnerability
    """
    new_vulnerability = False
    vulnerability = Vulnerability.query.get_or_404(id)
    form = VulnerabilityForm(obj=vulnerability)
    if form.validate_on_submit():
        vulnerability.title_vulnerability = form.title_vulnerability.data
        vulnerability.date_vulnerability = form.date_vulnerability.data
        vulnerability.cvs_code = form.cvs_code.data
        vulnerability.severity = form.severity.data
        vulnerability.risk = form.risk.data
        vulnerability.impact = form.impact.data
        vulnerability.ticket = form.ticket.data
        vulnerability.admin = form.admin.data
        vulnerability.recommanded_solution = form.recommanded_solution.data.capitalize()

        db.session.commit()
        flash('Edited Vulnerability  Saved successfully!')
        change_log('Vulnerability', 'Edit', vulnerability.id, vulnerability.title_vulnerability)

        
        return redirect(url_for('admin.list_vulnerabilities'))

    form.title_vulnerability.data = vulnerability.title_vulnerability
    form.date_vulnerability.data = vulnerability.date_vulnerability
    form.cvs_code.data = vulnerability.cvs_code
    form.severity.data = vulnerability.severity
    form.risk.data = vulnerability.risk
    form.impact.data = vulnerability.impact
    form.ticket.data = vulnerability.ticket
    form.admin.data = vulnerability.admin
    form.recommanded_solution.data = vulnerability.recommanded_solution

    return render_template('admin/vulnerabilities/vulnerability.html',
                           new_vulnerability=new_vulnerability, form=form,
                           vulnerability=vulnerability, title="Edit Server")

@admin.route('/vulnerability/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_vulnerability(id):
    """
    Delete a vulnerability from the database
    """
    check_admin()
    vulnerability = Vulnerability.query.get_or_404(id)
    db.session.delete(vulnerability)
    db.session.commit()
    flash('Vulnerability Deleted successfully.', 'danger')
    change_log('Vulnerability', 'Delete', vulnerability.id, vulnerability.title_vulnerability)

    return redirect(url_for('admin.list_vulnerabilities'))
   
@admin.route('/vulnerability/repport/<int:id>', methods=['GET', 'POST'])
@login_required
def vulnerability_repport(id):
    """
    Vulnerability Repport
    """
    vulnerability = Vulnerability.query.get_or_404(id)
    form = VulnerabilityForm(obj=vulnerability)
    form_note = Add_Note_vunerability(obj=vulnerability)

    return render_template('admin/vulnerabilities/vulnerability_repport.html', action="Show Rapport",
                           form=form,form_note=form_note, vulnerability=vulnerability, get_UserName=get_UserName, title="Show Rapport Vulnerabilite")


#######################################
###PROJECTS MANAGEMENT MODULE #####
#######################################
@admin.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """
    Add an project to the database
    """
    check_permission_assets(current_user.is_manager, current_user.is_admin)
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
        project_name = form.project_name.data.capitalize(),
        description = form.description.data.capitalize(),
        tags = form.tags.data,
        members = form.members.data,
        external_members = form.external_members.data,
        affectation_date = form.affectation_date.data,
        status = form.status.data,
        admin = form.admin.data)

        try:

            db.session.add(project)
            db.session.commit()
            flash('New Project added successfully.')
            change_log('Project', 'New', project.id, project.project_name)
            
            #FUNCTION TO SEND EMAIL FOR NEW PROJECT
            recipients = [project.admin.email, current_user.email]

            
            send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
            subject = (""" [INFRALINKER] - YOU HAVE A NEW PROJECT. """)
            html_template = render_template('email/email-project.html', project=project, send_time=send_time)
            send_email(recipients, subject, html_template)
    

        except Exception as e:
            flash('Failed to Save to DataBase: '+ str(e), 'danger')

        return redirect(url_for('admin.list_projects'))

    return render_template('admin/projects/project.html',new_project=new_project,get_members_name=get_members_name,get_contacts_fullname=get_contacts_fullname, get_tags_name=get_tags_name ,project="Add", form=form,
                           title="ADD NEW PROJECT")

@admin.route('/projects/list/', methods=['GET'])

@login_required
def list_projects():
    """
    List all projects
    """

    if current_user.is_admin:
        projects = Project.query.all()
        
    elif current_user.is_manager:
        projects = Project.query.join(Admin, Admin.id == Project.admin_id).filter(Admin.department_id == current_user.department_id).order_by(Project.affectation_date.desc()).all()
    else:
        projects = Project.query.filter_by(admin_id =current_user.id).all()
            

    return render_template('admin/projects/projects.html', projects=projects, get_tag_color=get_tag_color, title="LISTE ALL SERVERS")

@admin.route('/project/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    """
    Edit a project
    """
    
    check_permission_assets(current_user.is_manager, current_user.is_admin)
    
    new_project = False
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)

    if form.validate_on_submit() :

        project.project_name = form.project_name.data.capitalize()
        project.description = form.description.data
        project.affectation_date = form.affectation_date.data
        project.status = form.status.data
        project.members = form.members.data
        project.external_members = form.external_members.data
        project.tags = form.tags.data
        project.complete_date = datetime.datetime.now() if project.status == "COMPLETE" else "0000-00-00"
        project.admin = form.admin.data

        
        #SEND EMAIL IF PROJECT IS COMPLET
        send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

        if project.status == "COMPLETE" :  

            if not project.complete_date :
                    
                recipients = [project.admin.email, current_user.email]
                subject = " [INFRALINKER] - THIS PROJECT HAS BEEN COMPLETED. "
                html = render_template('email/email-project.html', project=project, send_time=send_time)
                send_email(recipients, subject, html)
                
                flash('PROJECT : '+ project.project_name +' COMPLETED.')

            else :
                pass
            
        else :
            flash('Edited Project Saved successfully!')

        db.session.commit()
        change_log('Project', 'Edit', project.id, project.project_name)
        return redirect(url_for('admin.list_projects'))
    
    form.project_name.data = project.project_name
    form.description.data = project.description
    form.affectation_date.data = project.affectation_date
    form.status.data = project.status
    form.members.data = project.members
    form.external_members.data = project.external_members
    form.tags.data = project.tags
    form.admin.data = project.admin

    return render_template('admin/projects/project.html',
                           new_project=new_project, form=form,
                           get_members_name=get_members_name,
                           get_contacts_fullname=get_contacts_fullname,
                           get_tags_name=get_tags_name,      
                           project=project, title="Edit Project")

# Function to check if there are dependencies for Multible Model
def check_project_dependencies(project_id):
    dependent_models = [Action, ProjectDocuments, Server]
    for model in dependent_models:
        if model.query.filter_by(project_id=project_id).first() is not None:
            return True
    return False

@admin.route('/project/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_project(id):
    """
    Delete a project from the database
    """
    check_permission_assets(current_user.is_manager, current_user.is_admin)

    if check_project_dependencies(id) :        
        flash("Cannot delete this Project with dependencies in Server/IP, Project Documents or Tasks. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_projects'))

    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project Deleted successfully.', 'danger')
    change_log('Project', 'Delete', project.id, project.project_name)

    
    return redirect(url_for('admin.list_projects'))

@admin.route('/details/project/<int:id>', methods=['GET'])
@login_required
def project_details(id):
    """
    Show Project Details
    """
    project = Project.query.get_or_404(id)
    project_documents = ProjectDocuments.query.filter_by(project_id =id).all()
    servers_list = Server.query.filter_by(project_id =id).all()
    tasks = Action.query.filter_by(project_id =id).all()

    return render_template('admin/projects/project_report.html',
        get_tag_color=get_tag_color, project=project,get_UserName=get_UserName,
        servers_list=servers_list,
        tasks=tasks,
        project_documents=project_documents,
        title="SHOW PROJECT DETAILS")

################################
## PROJECTS DOCUMENTS MODULE ###
################################

@admin.route('/project_document/<int:project_id>/new_document', methods=['GET', 'POST'])
@login_required
def new_project_document(project_id):
    """
    Add an project document to the database
    """

    project = Project.query.get(project_id)
    project_documents = ProjectDocuments.query.filter_by(project_id =project_id).all()
    form = ProjectDocumentsForm()
    
    if form.validate_on_submit():
        filename = secure_filename(form.document_name.data.filename)
        project_document = ProjectDocuments(
            document_name = filename,
            project=project,
            description = form.description.data.capitalize(),
            add_by = current_user.id,
            add_date = datetime.datetime.now())
        try:         
            form.document_name.data.save('app/static/uploads/projects/documents/'+ filename)
            db.session.add(project_document)
            db.session.commit()
            flash('You have successfully added a new Document.')
            change_log('Project Document '+ filename, 'New', project_document.id, project_document.document_name)
            
        except Exception as e:
            flash('Failed to Save to DataBase: '+ str(e), 'danger')

        return redirect(url_for('admin.new_project_document', project_id=project_document.project_id))

    return render_template('admin/projects/project_document.html',
            new_project=new_project,project=project,
            project_document="Add",project_documents=project_documents, form=form, get_UserName=get_UserName,
                           title="ADD NEW DOCUMENT")

@admin.route('/project_document/delete_document/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_project_document(id):
    """
    Delete a Document from the database
    """
    
    project_document = ProjectDocuments.query.get_or_404(id)
    db.session.delete(project_document)
    db.session.commit()
    
    os.remove("app/static/uploads/projects/documents/"+ project_document.document_name) # specifying the path of the file
    flash('Document Deleted successfully.')
    change_log('Project Document '+ project_document.document_name, 'Delete', project_document.id, project_document.document_name)

    
    return redirect(url_for('admin.new_project_document', project_id=project_document.project_id))

#######################################
### CONTRACTS MANAGEMENT MODULE #####
#######################################
@admin.route('/contract/new', methods=['GET', 'POST'])
@login_required
def new_contract():
    """
    Add new  contract to the database
    """
    check_permission_assets(current_user.control_contracts, current_user.is_admin)
    emailling_details = Emailling_config.query.get_or_404(1)

    form = ContractForm()
    if form.validate_on_submit():
        filename = secure_filename(form.contract_document.data.filename)
        contract = Contract(
            contract_number = form.contract_number.data.upper(),
            start_date = form.start_date.data,
            end_date = form.end_date.data,
            contract_document =  filename,
            notes = form.notes.data.capitalize(),
            supplier = form.supplier.data,
            add_by = current_user.id,
            add_date = datetime.datetime.now())

        try:
            
            if filename !='':
                form.contract_document.data.save('app/static/uploads/contracts/'+ filename)
            else:
                pass
            db.session.add(contract)
            db.session.commit()
            flash('You have successfully added a new Contract.')
            change_log('Contract', 'New', contract.id, contract.contract_number)
            
            #FUNCTION TO SEND EMAIL TO GROUPE FOR NEW CONTRACT
            emails_group=emailling_details.egroup_contract

            if emails_group :
                send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

                recipients = [email.strip() for email in emails_group.strip('()').split(',')]
                
                subject = (""" [INFRALINKER] - A NEW CONTRACT HAS BEEN ADDED. """)
                html_template = render_template('email/email-contract.html', contract=contract, send_time=send_time)
                send_email(recipients, subject, html_template)
            else :
                pass

        except Exception as e:
            flash('Failed to Save to database: '+ str(e), 'danger')

        return redirect(url_for('admin.list_contracts'))

    return render_template('admin/contracts/contract.html',new_contract=new_contract ,contract="Add", form=form,
                           title="ADD NEW CONTRACT")

@admin.route('/contracts/list/', methods=['GET'])

@login_required
def list_contracts():
    """
    List all contracts
    """
    contracts = Contract.query.all()

    return render_template('admin/contracts/contracts.html', contracts=contracts,date_comparator=date_comparator,check_expiration_date=check_expiration_date, title="LISTE ALL CONTRACTS")

@admin.route('/contract/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contract(id):
    """
    Edit a contract
    """
    
    new_contract = False
    contract = Contract.query.get_or_404(id)
    form = ContractForm(obj=contract)
    if form.validate_on_submit():
        filename = secure_filename(form.contract_document.data.filename)
        contract.contract_number = form.contract_number.data.upper()
        contract.start_date = form.start_date.data
        contract.end_date = form.end_date.data
        contract.contract_document =  filename 
        contract.notes = form.notes.data.capitalize()
        contract.supplier = form.supplier.data
        if filename !='':
            form.contract_document.data.save('app/static/uploads/contracts/'+ filename)
        else:
            pass
        db.session.commit()
        flash('Edited Contract Saved successfully!')
        change_log('Contract', 'Edit', contract.id, contract.contract_number)

        return redirect(url_for('admin.list_contracts'))

    form.contract_number.data = contract.contract_number
    form.start_date.data = contract.start_date
    form.end_date.data = contract.end_date
    form.contract_document.data = contract.contract_document
    form.notes.data = contract.notes
    form.supplier.data = contract.supplier

    return render_template('admin/contracts/contract.html',
                           new_contract=new_contract, form=form,
                           check_permission_assets=check_permission_assets,
                           contract=contract, title="Edit Contract")


def check_contract_dependencies(contract_id):    
    return Platform.query.filter_by(contract_id=contract_id).first() is not None

@admin.route('/contract/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_contract(id):
    """
    Delete a contract from the database
    """
    
    check_permission_assets(current_user.control_contracts, current_user.is_admin)

    if check_contract_dependencies(id) :        
        flash("Cannot delete this Contract with dependencies in Device. Please check before Deleting.", 'error')
        return redirect(url_for('admin.list_contracts'))


    contract = Contract.query.get_or_404(id)
    db.session.delete(contract)
    db.session.commit()

    path_file = "app/static/uploads/contracts/"+ contract.contract_document

    if contract.contract_document != None and os.path.isfile(path_file) :
        os.remove(path_file) # specifying the path of the file
    else:
        pass

    flash('Contract Deleted successfully.')
    change_log('Contract', 'Delete', contract.id, contract.contract_number)


    return redirect(url_for('admin.list_contracts'))
    
@admin.route('/details/contract/<int:id>', methods=['GET'])
@login_required
def contract_details(id):
    """
    Show contract Details
    """
    contract = Contract.query.get_or_404(id)
    devices_list = Platform.query.filter_by(contract_id = id).all()

    return render_template('admin/contracts/contract_details.html',
    get_tag_color=get_tag_color, contract=contract, devices_list=devices_list, get_UserName=get_UserName,
    check_expiration_date=check_expiration_date,
    title="SHOW CONTRACT DETAILS")

########################################
### APPLICATIONS MANAGEMENT MODULE #####
########################################

@admin.route('/application/new', methods=['GET', 'POST'])
@login_required
def new_application():
    """
    Add new  application to the database
    """
    check_permission_assets(current_user.control_applications, current_user.is_admin)

    form = ApplicationForm()
    if form.validate_on_submit():

        application =Application(
        app_name = form.app_name.data.upper(),
        app_version = form.app_version.data,
        app_description = form.app_description.data.capitalize(),
        app_ports = form.app_ports.data,
        tags = form.tags.data,
        add_by = current_user.id,
        add_date = datetime.datetime.now())

        try:
            db.session.add(application)
            db.session.commit()
            flash('You have successfully added a new Applications.')
            change_log('Application', 'New', application.id, application.app_name)
        except:
            flash('Error: Unknown.')

        return redirect(url_for('admin.list_applications'))

    return render_template('admin/applications/application.html',new_application=new_application ,application="Add", form=form,get_tags_name=get_tags_name,
                           title="ADD NEW APPLICATION")

@admin.route('/applications/list/', methods=['GET'])

@login_required
def list_applications():
    """
    List all applications
    """
    applications = Application.query.all()

    return render_template('admin/applications/applications.html', 
    applications=applications,
    get_tag_color=get_tag_color,get_UserName=get_UserName,
    date_comparator=date_comparator, title="LISTE ALL APPLICATIONS")

@admin.route('/application/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_application(id):
    """
    Edit a application
    """
    
    # check_permission_assets(current_user.control_applications, current_user.is_admin)
    
    new_application = False
    application = Application.query.get_or_404(id)
    form = ApplicationForm(obj=application)
    if form.validate_on_submit():

        application.app_name = form.app_name.data.upper()
        application.app_version = form.app_version.data
        application.app_description = form.app_description.data.capitalize()
        application.app_ports = form.app_ports.data
        application.tags = form.tags.data
        # contract.platform = form.platform.data

        db.session.commit()
        change_log('Application', 'Edit', application.id, application.app_name)
        flash('Edited Application Saved successfully!')

        return redirect(url_for('admin.list_applications'))

    form.app_name.data = application.app_name
    form.app_version.data = application.app_version
    form.app_description.data = application.app_description
    form.app_ports.data = application.app_ports
    form.tags.data = application.tags
    

    return render_template('admin/applications/application.html',
                           new_application=new_application, form=form,
                           check_permission_assets=check_permission_assets,
                           get_tags_name=get_tags_name,
                           application=application, title="Edit application")

@admin.route('/application/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_application(id):
    """
    Delete a application from the database
    """
    
    check_permission_assets(current_user.control_applications, current_user.is_admin)
    application = Application.query.get_or_404(id)
    change_log('Application', 'Delete', application.id, application.app_name)
    db.session.delete(application)
    db.session.commit()
    flash('Application Deleted successfully.', 'danger')

    return redirect(url_for('admin.list_applications'))
    

########################################
## SETTINGS VIEWS TO CONFIGURE SMTP ####
########################################
@admin.route('/settings/edit_settings', methods=['GET', 'POST'])
@login_required
def settings_config():
    """
    Edit settings
    """
    
    check_admin()
    
    var_exists = db.session.query(Emailling_config.query.filter(Emailling_config.id == 1).exists()).scalar()

    if not var_exists :
        form = SMTPConfigForm()
        if form.validate_on_submit():

            smtp_config = Emailling_config(
            egroup_vulnerability = form.egroup_vulnerability.data,
            egroup_ticket = form.egroup_ticket.data,
            egroup_contract = form.egroup_contract.data)
            db.session.add(smtp_config)
            db.session.commit()
            flash('Config Saved successfully!')
            return redirect(url_for('home.admin_dashboard'))

        return render_template('admin/settings/settings.html',form=form,title="Edit Settings")

    else :
        smtp_config = Emailling_config.query.get_or_404(1)
        form = SMTPConfigForm(obj=smtp_config)
        if form.validate_on_submit():

            smtp_config.egroup_vulnerability = form.egroup_vulnerability.data
            smtp_config.egroup_ticket = form.egroup_ticket.data
            smtp_config.egroup_contract = form.egroup_contract.data
            db.session.commit()
            flash('Edited Config Saved successfully!')
            
            return redirect(url_for('home.admin_dashboard'))

        form.egroup_vulnerability.data = smtp_config.egroup_vulnerability
        form.egroup_ticket.data = smtp_config.egroup_ticket
        form.egroup_contract.data = smtp_config.egroup_contract

        return render_template('admin/settings/settings.html',form=form,smtp_config=smtp_config, title="Edit SMTP Settings")
                           
###############################################
## CHANGE LOG AND HISTORY OFF MODIFICATION ####
###############################################
@admin.route('/changelog/history/', methods=['GET'])
@login_required
def list_changelogs():
    """
    View All Modifications
    """
    check_admin()
    changelogs = ChangeLog.query.order_by(ChangeLog.change_date.desc()).all()

    return render_template('admin/changelog/change_logs.html', changelogs=changelogs,get_UserName=get_UserName, title="LISTE ALL CHANGE")

# Endpoint for removing data based on the selected time frame
@admin.route('/remove_data/<int:months>')
@login_required
def remove_logs(months):
    # Calculate the date threshold
    threshold_date = datetime.datetime.now() - timedelta(days=30 * months)

    # Query and remove data using SQLAlchemy
    records_to_delete = ChangeLog.query.filter(ChangeLog.change_date < threshold_date).all()

    for record in records_to_delete:
        db.session.delete(record)

    db.session.commit()
    flash(f'Data older than {months} months removed.', "info")
            
    return redirect(url_for('admin.list_changelogs'))

    #return f'Data older than {months} months removed.'
#######################################
## IMPORT CSV DATA ####################
#######################################

#### IP'S / SERVERS IMPORT #########
def insert_servers_data(data):
    """
    Insert servers data into the database.
    Parameters:
    data (DataFrame): Data to insert into the database.
    """
    connection = mydb.raw_connection()
    mycursor = connection.cursor()
    try:
        for i, row in data.iterrows():
            sql = "INSERT INTO infralinker_db.servers (server_name, operating_system, os_version, type, tags, ip_address, applications_list, department_id, notes,vitality_classification, network_id, platform_id, add_by, add_date, project_id) VALUES (%s,%s, %s,%s,%s, %s, %s, %s, %s, %s ,%s, %s,%s,%s,%s)"
            value = (row['server_name'], row['operating_system'], row['os_version'], row['type'], row['ip_address'],row['tags'], row['applications_list'], row['department_id'], row['notes'],row['vitality_classification'], row['network_id'], row['platform_id'],row['add_by'],row['add_date'], row['project_id'])
            mycursor.execute(sql, value)
            connection.commit()
        flash('Servers Data Imported successfully')

    except Exception as e:
            connection.rollback()  # Rollback in case of error
            flash('Failed to Save to DataBase: ' + str(e), 'danger')
    finally:
        mycursor.close()
        connection.close()  # Ensure the connection is closed

@admin.route('/import_csv/new_data_for_servers', methods=['GET', 'POST'])
@login_required
def import_servers_data():
    """
    IMPORT CSV SERVERS DATA TO THE DATABASE
    """          
    check_admin()
    form = ImportCSVForm()  # Assuming this form has both a file field and a textarea
    
    col_names = ['server_name', 'operating_system', 'os_version', 'type','tags', 'ip_address', 'applications_list', 'department_id', 'notes','vitality_classification', 'network_id', 'platform_id','add_by','add_date','project_id']

    if form.validate_on_submit():
        if form.import_data.data:  # If a file is uploaded
            csvData = pd.read_csv(io.StringIO(form.import_data.data.read().decode('utf-8')), names=col_names, sep=';', skiprows=1)
            insert_servers_data(csvData)
        elif form.text_data.data:  # Assuming `text_data` is the name of your textarea field
            # Process text input as if it was a CSV file
            textData = pd.read_csv(io.StringIO(form.text_data.data), names=col_names, sep=';', skiprows=1)
            insert_servers_data(textData)
        else:
            flash('NO DATA PROVIDED !', 'danger')
    return render_template('admin/import/csv_servers.html', form=form, title="IMPORT SERVERS DATA")

#### DEVICES IMPORT #############
def insert_devices_data(data):
    """
    Insert devices data into the database.
    Parameters:
    data (DataFrame): Data to insert into the database.
    """
    connection = mydb.raw_connection()
    mycursor = connection.cursor()
    try:
        for i, row in data.iterrows():
            sql = "INSERT INTO infralinker_db.platforms (platform_name, serial_number, supplier_id, rack_id, u_hight, u_position, tags, power_supply, production_date, end_warranty_date, network_identity, add_by, add_date, notes, contract_id, device_role_id) VALUES (%s,%s, %s,%s,%s, %s, %s, %s, %s, %s ,%s, %s, %s, %s, %s, %s)"
            value = (row['platform_name'], row['serial_number'], row['supplier_id'], row['rack_id'], row['u_hight'], row['u_position'], row['tags'], row['power_supply'], row['production_date'], row['end_warranty_date'], row['network_identity'], row['add_by'], row['add_date'], row['notes'], row['contract_id'], row['device_role_id'])
            mycursor.execute(sql, value)
            connection.commit()
        flash('Devices Data Imported successfully')

    except Exception as e:
            connection.rollback()  # Rollback in case of error
            flash('Failed to Save to DataBase: ' + str(e), 'danger')
    finally:
        mycursor.close()
        connection.close()  # Ensure the connection is closed

@admin.route('/import_csv/new_data_for_platforms', methods=['GET', 'POST'])
@login_required
def import_platforms_data():
    """
    IMPORT CSV PLATFORMS DATA TO THE DATABASE
    """      
    check_admin()
    form = ImportCSVForm()  # Assuming this form has both a file field and a textarea

    col_names = ['platform_name', 'serial_number', 'supplier_id', 'rack_id', 'u_hight', 'u_position', 'tags', 'power_supply', 'production_date', 'end_warranty_date', 'network_identity', 'add_by', 'add_date', 'notes', 'contract_id', 'device_role_id']

    if form.validate_on_submit():
        if form.import_data.data:  # If a file is uploaded
            csvData = pd.read_csv(io.StringIO(form.import_data.data.read().decode('utf-8')), names=col_names, sep=';', skiprows=1)
            insert_devices_data(csvData)
        elif form.text_data.data:  # Assuming `text_data` is the name of your textarea field
            # Process text input as if it was a CSV file
            textData = pd.read_csv(io.StringIO(form.text_data.data), names=col_names, sep=';', skiprows=1)
            insert_devices_data(textData)
        else:
            flash('NO DATA PROVIDED !', 'danger')
    return render_template('admin/import/csv_platforms.html', form=form, title="IMPORT DEVICES DATA")

#### NETWORKS IMPORT ##############

def insert_networks_data(data):
    """
    Insert networks data into the database.
    Parameters:
    data (DataFrame): Data to insert into the database.
    """
    connection = mydb.raw_connection()
    mycursor = connection.cursor()
    try:
        for i, row in data.iterrows():
            sql = "INSERT INTO infralinker_db.networks (net_name, tag, mask, gatway, net_notes, tags , add_by, add_date, datacenter_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            value = (row['net_name'], row['tag'], row['mask'], row['gatway'], row['net_notes'], row['tags'], row['add_by'], row['add_date'], row['datacenter_id'])
            mycursor.execute(sql, value)
            connection.commit()
        flash('Networks Data Imported successfully')

    except Exception as e:
            connection.rollback()  # Rollback in case of error
            flash('Failed to Save to DataBase: ' + str(e), 'danger')
    finally:
        mycursor.close()
        connection.close()  # Ensure the connection is closed

@admin.route('/import_csv/new_data_for_networks', methods=['GET', 'POST'])
@login_required
def import_networks_data():
    """
    IMPORT CSV NETWORKS DATA TO THE DATABASE
    """       
    check_admin()
    form = ImportCSVForm()  # Assuming this form has both a file field and a textarea

    col_names = ['net_name', 'tag', 'mask', 'gatway', 'net_notes', 'tags', 'add_by', 'add_date', 'datacenter_id']

    if form.validate_on_submit():
        if form.import_data.data:  # If a file is uploaded
            csvData = pd.read_csv(io.StringIO(form.import_data.data.read().decode('utf-8')), names=col_names, sep=';', skiprows=1)
            insert_networks_data(csvData)
        elif form.text_data.data:  # Assuming `text_data` is the name of your textarea field
            # Process text input as if it was a CSV file
            textData = pd.read_csv(io.StringIO(form.text_data.data), names=col_names, sep=';', skiprows=1)
            insert_networks_data(textData)
        else:
            flash('NO DATA PROVIDED !', 'danger')
    return render_template('admin/import/csv_networks.html', form=form, title="IMPORT NETWORKS DATA")

#### RACKS IMPORT ################### 

def insert_racks_data(data):
    """
    Insert racks data into the database.
    Parameters:
    data (DataFrame): Data to insert into the database.
    """
    connection = mydb.raw_connection()
    mycursor = connection.cursor()
    try:
        for i, row in data.iterrows():
            sql = "INSERT INTO infralinker_db.racks (r_name, ru_hight, installation_date, r_notes, datacenter_id, add_by, add_date, tags, r_position) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            value = (row['r_name'], row['ru_hight'], row['installation_date'], row['r_notes'], row['datacenter_id'], row['add_by'], row['add_date'], row['tags'], row['r_position'])
            mycursor.execute(sql, value)
            connection.commit()
        flash('Racks Data Imported successfully')
    except Exception as e:
            connection.rollback()  # Rollback in case of error
            flash('Failed to Save to DataBase: ' + str(e), 'danger')
    finally:
        mycursor.close()
        connection.close()  # Ensure the connection is closed

@admin.route('/import_csv/new_data_for_racks', methods=['GET', 'POST'])
@login_required
def import_racks_data():
    check_admin()
    form = ImportCSVForm()  # Assuming this form has both a file field and a textarea

    col_names = ['r_name', 'ru_hight', 'installation_date', 'r_notes', 'datacenter_id', 'add_by', 'add_date', 'tags', 'r_position']

    if form.validate_on_submit():
        if form.import_data.data:  # If a file is uploaded
            csvData = pd.read_csv(io.StringIO(form.import_data.data.read().decode('utf-8')), names=col_names, sep=';', skiprows=1)
            insert_racks_data(csvData)
        elif form.text_data.data:  # Assuming `text_data` is the name of your textarea field
            # Process text input as if it was a CSV file
            textData = pd.read_csv(io.StringIO(form.text_data.data), names=col_names, sep=';', skiprows=1)
            insert_racks_data(textData)
        else:
            flash('NO DATA PROVIDED !', 'danger')
    return render_template('admin/import/csv_racks.html', form=form, title="IMPORT RACKS DATA")
    

#### APPLICATIONS  IMPORT #########
def insert_applications_data(data):
    """
    Insert applications data into the database.
    Parameters:
    data (DataFrame): Data to insert into the database.
    """
    connection = mydb.raw_connection()
    mycursor = connection.cursor()
    try:
        for i, row in data.iterrows():
            sql = "INSERT INTO infralinker_db.applications (app_name, app_version, app_description, app_ports, tags, add_by, add_date) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            value = (row['app_name'], row['app_version'], row['app_description'], row['app_ports'], row['tags'], row['add_by'], row['add_date'])
            mycursor.execute(sql, value)
            connection.commit()
        flash('Applications Data Imported successfully')

    except Exception as e:
            connection.rollback()  # Rollback in case of error
            flash('Failed to Save to DataBase: ' + str(e), 'danger')
    finally:
        mycursor.close()
        connection.close()  # Ensure the connection is closed

@admin.route('/import_csv/new_data_for_applications', methods=['GET', 'POST'])
@login_required
def import_applications_data():
    """
    IMPORT CSV APPS DATA TO THE DATABASE
    """          
    check_admin()
    form = ImportCSVForm()  # Assuming this form has both a file field and a textarea
    
    col_names = ['app_name','app_version','app_description','app_ports','tags','add_by','add_date']

    if form.validate_on_submit():
        if form.import_data.data:  # If a file is uploaded
            csvData = pd.read_csv(io.StringIO(form.import_data.data.read().decode('utf-8')), names=col_names, sep=';', skiprows=1)
            insert_applications_data(csvData)
        elif form.text_data.data:  # Assuming `text_data` is the name of your textarea field
            # Process text input as if it was a CSV file
            textData = pd.read_csv(io.StringIO(form.text_data.data), names=col_names, sep=';', skiprows=1)
            insert_applications_data(textData)
        else:
            flash('NO DATA PROVIDED !', 'danger')
    return render_template('admin/import/csv_applications.html', form=form, title="IMPORT APPLICATIONS DATA")

