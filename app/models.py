#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Author: Abdellah ALAOUI ISMAILI
#   
#  Project Name: InfraLinker
#  Project web Site: https://infralinker.net

"""
This is Model file containing the database models for InfraLinker App, keeping everything in its proper place.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import SelectMultipleField
from app import db, login_manager
from config import app_config
import app, sys
from sqlalchemy import text
import importlib as il

il.reload(sys)

##################CLASS FOR MANAGING USERS#####################
class Admin(UserMixin, db.Model):
    """
    USERS TABLE
    """
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(60), index=True)
    lastname = db.Column(db.String(60), index=True)
    email = db.Column(db.String(60), index=True, unique=True)
    phone =  db.Column(db.String(20), index=True, unique=True)
    function = db.Column(db.String(100), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, index=True)
    is_manager = db.Column(db.Boolean, default=False, index=True) #If user is manager he can create his own projects (only project)
    control_racks = db.Column(db.Boolean, default=False, index=True) #Can add or remove racks
    control_platforms = db.Column(db.Boolean, default=False, index=True) #Can Add or remove platforms ( Hardware/ Software )
    control_networks = db.Column(db.Boolean, default=False, index=True) #Can Add or remove networks or VLAN
    control_servers = db.Column(db.Boolean, default=False, index=True) #Can Add or remove servers or IP addresses
    control_contracts = db.Column(db.Boolean, default=False, index=True)    #Can Add or remove Contract
    control_applications = db.Column(db.Boolean, default=False, index=True)    #Can Add or remove Application
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    change_password = db.Column(db.Boolean, default=False) #user must change password
    last_seen = db.Column(db.DateTime, nullable = True)

    tickets = db.relationship('Ticket', backref='admin',
                                lazy='dynamic')
    vulnerabilities = db.relationship('Vulnerability', backref='admin',
                                lazy='dynamic')
    projects = db.relationship('Project', backref='admin',
                                lazy='dynamic')
    interventions = db.relationship('Intervention', backref='admin',
                                lazy='dynamic')
    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def __repr__(self):
        return '<Admin: {}>'.format(self.id)

# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

class Department(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True)
    description = db.Column(db.String(1000))

    admins = db.relationship('Admin', backref='department',
                                lazy='dynamic')

    servers = db.relationship('Server', backref='department',
                            lazy='dynamic')

    def __repr__(self):
        return '<Department: {}>'.format(self.name)

class Supplier(db.Model):
    """
    SUPPLIERS TABLES
    """

    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    notes = db.Column(db.String(2000))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)

    tickets = db.relationship('Ticket', backref='supplier',
                                lazy='dynamic')

    platforms = db.relationship('Platform', backref='supplier',
                                lazy='dynamic')

    contacts = db.relationship('Contact', backref='supplier',
                                lazy='dynamic')

    contracts = db.relationship('Contract', backref='supplier',
                                lazy='dynamic')

    def __repr__(self):
        return '<Supplier: {}>'.format(self.id)

class Contact(db.Model):
    """
    CONTACTS TABLES
    """

    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    notes = db.Column(db.String(1000))
    

    interventions = db.relationship('Intervention', backref='contact',
                                lazy='dynamic')

    def __repr__(self):
        return '<Contact: {}>'.format(self.id)

class Ticket(db.Model):
    """
    TICKETS TABLE
    """

    __tablename__ = 'tickets'


    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(100))
    open_date = db.Column(db.Date, nullable = False)
    description = db.Column(db.String(5000))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    priority = db.Column(db.String(100))
    impact = db.Column(db.String(100))
    status = db.Column(db.String(100))
    resolution_date = db.Column(db.Date)
    comments = db.Column(db.String(5000))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)


    interventions = db.relationship('Intervention', backref='ticket',
                                lazy='dynamic')

    vulnerabilities = db.relationship('Vulnerability', backref='ticket',
                                lazy='dynamic')

    def __repr__(self):
        return '<Ticket: {}>'.format(self.id)

class Platform(db.Model):
    """
    PLATFORMS TABLES
    """

    __tablename__ = 'platforms'

    id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(200), nullable = False)
    serial_number = db.Column(db.String(250), nullable = True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    rack_id = db.Column(db.Integer, db.ForeignKey('racks.id'))
    u_hight = db.Column(db.Integer)
    u_position = db.Column(db.String(50), nullable = True)
    tags = db.Column(db.String(500))
    power_supply = db.Column(db.Integer)
    production_date = db.Column(db.Date, nullable = False)
    end_warranty_date = db.Column(db.Date, nullable = True)
    network_identity = db.Column(db.String(100), nullable = True)
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)
    notes = db.Column(db.String(5000))
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    device_role_id = db.Column(db.Integer, db.ForeignKey('device_roles.id'))

    servers = db.relationship('Server', backref='platform',
                                lazy='dynamic')

    tickets = db.relationship('Ticket', backref='platform',
                                lazy='dynamic')

    def __repr__(self):
        return '<Platform: {}>'.format(self.id)

class Device_Role(db.Model):
    """
    DEVICE ROLE TABLES
    """

    __tablename__ = 'device_roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    description = db.Column(db.String(5000))
    device_color = db.Column(db.String(10))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)

    platforms = db.relationship('Platform', backref='device_role',
                                lazy='dynamic')
    def __repr__(self):
       return '<Device_Role: {}>'.format(self.id)

class Vulnerability(db.Model):
    """
    VULNERABILITIES TABLE.
    """
    __tablename__='vulnerabilities'

    id = db.Column(db.Integer, primary_key=True)
    title_vulnerability = db.Column(db.String(500))
    date_vulnerability = db.Column(db.Date, nullable = False)
    cvs_code = db.Column(db.String(200))
    severity = db.Column(db.String(100))
    risk = db.Column(db.String(100))
    impact = db.Column(db.String(5000))
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    recommanded_solution = db.Column(db.String(5000))
    vulnerabitlity_note = db.Column(db.String(5000))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)

    def __repr__(self):
        return '<Vulnerability: {}>'.format(self.id)

class Intervention(db.Model):
    """
    INTERVENTIONS TABLE
    """

    __tablename__ = 'interventions'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    intervention_date = db.Column(db.Date, nullable = False)
    comment = db.Column(db.String(5000))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))

    def __repr__(self):
        return '<Intervention: {}>'.format(self.id)

class Project(db.Model):
    """
    PROJECTS TABLE
    """

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(1000))
    description = db.Column(db.String(5000))
    affectation_date = db.Column(db.Date, nullable = False)
    status = db.Column(db.String(100))
    tags = db.Column(db.String(500))
    members = db.Column(db.String(2500))
    external_members = db.Column(db.String(2500))
    complete_date = db.Column(db.Date)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))

    actions = db.relationship('Action', backref='project',
                                lazy='dynamic')

    project_documents = db.relationship('ProjectDocuments', backref='project',
                                lazy='dynamic')

    servers = db.relationship('Server', backref='project',
                                lazy='dynamic')

    def __repr__(self):
        return '<Project: {}>'.format(self.id)

class ProjectDocuments(db.Model):
    """
    PROJECT DOCUMENTS TABLE
    """

    __tablename__ = 'project_documents'

    id = db.Column(db.Integer, primary_key=True)
    document_name = db.Column(db.String(500))
    description = db.Column(db.String(5000))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))


    def __repr__(self):
        return '<ProjectDocuments: {}>'.format(self.id)

class Action(db.Model):
    """
    ACTIONS TABLE
    """

    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    description =   db.Column(db.String(5000))
    status = db.Column(db.String(100))
    execution_date = db.Column(db.Date, nullable = True)
    finish_date = db.Column(db.Date, nullable = True)

    def __repr__(self):
        return '<Action: {}>'.format(self.id)

class Datacenter(db.Model):
    """
    DATACENTERS TABLES
    """

    __tablename__ = 'datacenters'

    id = db.Column(db.Integer, primary_key=True)
    dc_name = db.Column(db.String(100))
    dc_address = db.Column(db.String(500))
    dc_type = db.Column(db.String(50))
    dc_city = db.Column(db.String(100))
    dc_country = db.Column(db.String(100))
    dc_phone = db.Column(db.String(20))
    dc_notes = db.Column(db.String(5000))

    racks = db.relationship('Rack', backref='datacenter',
                            lazy='dynamic')
    networks = db.relationship('Network', backref='datacenter',
                            lazy='dynamic')

class Rack(db.Model):
    """
    Racks TABLES
    """

    __tablename__ = 'racks'

    id = db.Column(db.Integer, primary_key=True)
    r_name = db.Column(db.String(100))
    ru_hight = db.Column(db.Integer)
    r_position = db.Column(db.String(100))
    installation_date = db.Column(db.Date, nullable = False)
    r_notes = db.Column(db.String(2000))
    datacenter_id = db.Column(db.Integer, db.ForeignKey('datacenters.id'))
    tags = db.Column(db.String(500))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)

    platforms = db.relationship('Platform', backref='rack',
                                lazy='dynamic')

class Network(db.Model):
    """
    NETWORKS TABLES
    """

    __tablename__ = 'networks'

    id = db.Column(db.Integer, primary_key=True)
    net_name = db.Column(db.String(200))
    tag = db.Column(db.Integer)
    mask = db.Column(db.String(20))
    gatway = db.Column(db.String(20))
    net_notes = db.Column(db.String(5000))
    tags = db.Column(db.String(500))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)
    datacenter_id = db.Column(db.Integer, db.ForeignKey('datacenters.id'))

    servers = db.relationship('Server', backref='network',
                            lazy='dynamic')

class Server(db.Model):
    """
    SERVERS TABLE
    """

    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(100))
    operating_system = db.Column(db.String(20))
    os_version = db.Column(db.String(50))
    type = db.Column(db.String(20))
    ip_address = db.Column(db.String(20))
    vitality_classification = db.Column(db.String(20))
    applications_list =  db.Column(db.String(5000))
    tags = db.Column(db.String(500))
    notes =  db.Column(db.String(5000))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)
    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    def __repr__(self):
        return '<Server: {}>'.format(self.name)

class Contract(db.Model):
    """
    CONTRACTS TABLE
    """
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable = False)
    end_date = db.Column(db.Date, nullable = False)
    contract_document = db.Column(db.String(500))
    notes =  db.Column(db.String(10000))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))

    platforms = db.relationship('Platform', backref='contract',
                                lazy='dynamic')

class Tag(db.Model):
    """
    TAGS TABLES
    """
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(50), unique=True)
    tag_description = db.Column(db.String(500))
    tag_color = db.Column(db.String(10))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)

class Application(db.Model):
    """
    APPLICATIONS TABLES
    """
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100))
    app_version =  db.Column(db.String(100))
    app_description = db.Column(db.String(2000))
    app_ports =  db.Column(db.String(200))
    tags = db.Column(db.String(200))
    add_by = db.Column(db.Integer)
    add_date = db.Column(db.DateTime, nullable = False)

    # servers = db.relationship('Server', backref='application',
    #                             lazy='dynamic')

    def __repr__(self):
        return '<Application: {}>'.format(self.name)

class ChangeLog(db.Model):
    """
    TABLE FOR LOG CHANGE
    """
    __tablename__ = 'changelog'
    id = db.Column(db.Integer, primary_key=True)
    change_date = db.Column(db.DateTime, nullable = False)
    user_id = db.Column(db.Integer, index=True)
    change_type = db.Column(db.String(500), index=True)
    id_type = db.Column(db.Integer)
    name_type = db.Column(db.String(100))
    action = db.Column(db.String(100), index=True)
    
class Emailling_config(db.Model):
    """
    TABLE OF SMTP SERVER CONFIG AND EMAILING GROUP BY CATEGORIES
    """   
    __tablename__ = 'emailling_config'
    id = db.Column(db.Integer, primary_key=True)
    egroup_vulnerability =  db.Column(db.String(5000))
    egroup_ticket =  db.Column(db.String(5000))
    egroup_contract =  db.Column(db.String(5000))

class Select2MultipleField(SelectMultipleField):

    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = ", ".join(valuelist)
        else:
            self.data = ""
