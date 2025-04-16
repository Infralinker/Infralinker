#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Author: Abdellah ALAOUI ISMAILI
#   
#  Project Name: InfraLinker
#  Project web Site: https://infralinker.net
"""
This is Form file.
"""

from flask_wtf import FlaskForm
from flask import  current_app, flash
from wtforms import StringField, SubmitField, IntegerField, RadioField, TextAreaField,ValidationError, SelectField, BooleanField, SelectMultipleField, DateTimeField, HiddenField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, EqualTo , InputRequired, IPAddress
from wtforms_validators import AlphaDash, AlphaSpace, Alpha, ValidationError
from datetime import datetime, date
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Admin, Supplier, ProjectDocuments, Contract,Device_Role, Ticket, Platform, Vulnerability,Tag, Intervention, Project, Action, Contact,Datacenter, Rack, Select2MultipleField, Network, Server, Department
from ..library.ip_calculator import check_ip_in_network_by_id
from wtforms.fields import DateField, TelField
from flask_ckeditor import CKEditorField
import re
__author__ = 'Abdellah ALAOUI ISMAILI'
__version__ = '1.0.1'

def NetMask(form, field):
    subnet_lists = ["255.255.255.252","255.255.255.248","255.255.255.240","255.255.255.224",
                    "255.255.255.192","255.255.255.128","255.255.255.0","255.255.254.0","255.255.252.0","255.255.248.0",
                    "255.255.240.0","255.255.224.0","255.255.192.0","255.255.128.0","255.255.0.0","255.254.0.0","255.252.0.0",
                    "255.248.0.0","255.240.0.0","255.224.0.0","255.192.0.0","255.128.0.0","255.0.0.0","254.0.0.0","252.0.0.0",
                    "248.0.0.0","240.0.0.0","224.0.0.0","192.0.0.0","128.0.0.0","0.0.0.0"]
    if not (field.data in subnet_lists):
        raise ValidationError("NetMask Not Valide !")

def get_net_name_tag_label(network):
    return f"{network.id} - {network.net_name}  -  {network.tag}  -  {network.mask}  -  {network.gatway}"

def get_admin_complet_name_label(user):
    return f"{user.firstname} {user.lastname}"

def get_contract_info_label(contract):
    return f"{contract.contract_number} - {contract.supplier.company_name}"

def is_password_complex(form, field):
    """
    Custom validation function to check password complexity.
    """
    password = field.data

    # Length between 6 and 12 characters
    if not (6 <= len(password) <= 12):
        raise ValidationError('Password must be between 8 and 12 characters long.')

    # At least one uppercase letter
    if not any(char.isupper() for char in password):
        raise ValidationError('Password must contain at least one uppercase letter.')

    # At least one digit
    if not any(char.isdigit() for char in password):
        raise ValidationError('Password must contain at least one digit.')

    # Additional complexity requirements can be added here

def validate_u_position(form, field):
        position = field.data
        if not position or '-' not in position:
            raise ValidationError('Position must be in the format "from-to" (e.g., 5-10)')
        parts = position.split('-')
        if len(parts) != 2:
            raise ValidationError('Invalid position format')
        try:
            from_pos, to_pos = map(int, parts)
            if from_pos >= to_pos:
                raise ValueError
        except ValueError:
            raise ValidationError('Invalid position range or non-numeric values')

class AdminRegistrationForm(FlaskForm):
    """
    CREATION OF ADMIN COUNTS
    """
    csrf = True 
    firstname = StringField('FIRSTNAME :', validators=[DataRequired(), Alpha()])
    lastname = StringField('LASTNAME :', validators=[DataRequired(),  Alpha()])
    email = StringField('E-MAIL :', validators=[DataRequired(), Email()])
    phone = TelField('PHONE :', validators=[DataRequired()])
    function = StringField('POSTE :', validators=[DataRequired()])
    department = QuerySelectField('DEPARTMENT :', allow_blank=True, query_factory=lambda: Department.query.all(), get_label="name")
    password = PasswordField('PASSWORD :', validators=[DataRequired(),EqualTo('confirm_password'), is_password_complex])
    confirm_password = PasswordField('CONFIRM PASSWORD :')
    is_admin = BooleanField('IS ADMINISTRATOR')
    is_manager = BooleanField('IS MANAGER OF DEPARTMENT')
    change_password = BooleanField("""USER MUST CHANGE THE PASSWORD !""")    
    control_racks = BooleanField('THIS USER CAN CONTROL RACKS')
    control_platforms = BooleanField('THIS USER CAN CONTROL PLATFORMS')
    control_networks = BooleanField('THIS USER CAN CONTROL NETWORKS')
    control_servers = BooleanField('THIS USER CAN CONTROL SERVERS')
    control_applications = BooleanField('THIS USER CAN CONTROL APPLICATIONS')
    control_contracts = BooleanField('THIS USER CAN CONTROL CONTRACTS')

    submit = SubmitField('SAVE USER')

    def validate_email(self, field):
        if Admin.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use!')

    def validate_phone(self, field):
        if Admin.query.filter_by(phone=field.data).first():
            raise ValidationError('Phone is already in use!')

class AdminEditForm(FlaskForm):
    """
    EDIT ADMIN FORM
    """
    origin_email = HiddenField()
    origin_phone = HiddenField()
    firstname = StringField('NOM :', validators=[DataRequired()])
    lastname = StringField('PRENOM :', validators=[DataRequired()])
    email = StringField('E-MAIL :', validators=[DataRequired(), Email()])
    phone = StringField('PHONE :', validators=[DataRequired()])
    function = StringField('POSTE :', validators=[DataRequired()])
    department = QuerySelectField('DEPARTMENT :', allow_blank=True, query_factory=lambda: Department.query.all(), get_label="name")
    is_admin = BooleanField('IS ADMINISTRATOR')
    is_manager = BooleanField('IS MANAGER OF DEPARTMENT')
    change_password = BooleanField("USER MUST CHANGE THE PASSWORD")
    control_racks = BooleanField('THIS USER CAN CONTROL RACKS')
    control_platforms = BooleanField('THIS USER CAN CONTROL PLATFORMS')
    control_networks = BooleanField('THIS USER CAN CONTROL NETWORKS')
    control_servers = BooleanField('THIS USER CAN CONTROL SERVERS')
    control_contracts = BooleanField('THIS USER CAN CONTROL CONTRACTS')
    control_applications = BooleanField('THIS USER CAN CONTROL APPLICATIONS')
    
    submit = SubmitField('SAVE CHANGE')

    #Check if Email Existe
    def validate_email(self, field):
        OrgEmail = Admin.query.filter_by(email=field.data).first()
        if OrgEmail and self.email.data != self.origin_email.data :
            raise ValidationError('Email is already in use!')
    #Check if Phone Number Existe
    def validate_phone(self, field):
        Orgphone = Admin.query.filter_by(phone=field.data).first()
        if Orgphone and self.phone.data != self.origin_phone.data :
            raise ValidationError('Phone is already in use!')

class DepartmentForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    name = StringField('DEPARTMENT NAME :', validators=[DataRequired()])
    description = StringField('DESCRIPTION :', validators=[DataRequired()])
    submit = SubmitField('SAVE')

class DatacenterForm(FlaskForm):
    """
    DATACENTER FORM
    """
    origin_dc_name = HiddenField()
    dc_name = StringField('DC NAME :', validators=[DataRequired()])
    dc_type = SelectField('TYPE (ON-PREMISE / CLOUD)  :', choices =[
        ('ON-PREMISE','On-Premises Infrastructure'),
        ('AWS','Amazon Web Services (AWS)'),
        ('AZURE','Microsoft Azure '),
        ('GCP','Google Cloud Platform (GCP)'),
        ('ALIBABA','Alibaba Cloud'),
        ('ORACLE','Oracle Cloud'),
        ('IBM','IBM Cloud (Kyndryl)'),
        ('TENCENT','Tencent Cloud'),
        ('OVH','OVHcloud'),
        ('DIGITALOCEAN','DigitalOcean'),
        ('LINODE','Linode (Akamai)'),
        ('OTHER','Other Cloud Provider')
        ])
    dc_address = StringField('DC ADDRESS :',validators=[DataRequired()])
    dc_city = StringField('CITY :', validators=[DataRequired()])
    dc_country = StringField('COUNRTY :', validators=[DataRequired()])
    dc_phone = StringField('PHONE :', validators=[DataRequired()])
    submit = SubmitField('SAVE')

    def validate_dc_name(self, field):
        dcName = Datacenter.query.filter_by(dc_name=field.data).first()
        if dcName and self.dc_name.data != self.origin_dc_name.data:
            raise ValidationError('DataCenter Name is already in use!')

class RackForm(FlaskForm):
    """
    RACK FORM
    """
    origin_rack = HiddenField()
    r_name = StringField('RACK NAME :', validators=[DataRequired()])
    ru_hight = StringField('RU HIGHT :',validators=[DataRequired()])
    r_position = StringField('RACK POSITION (FLOOR / ROW / RACK) :', render_kw= {"placeholder":"1/1/16", "class":"form-control"})
    installation_date = DateField("INSTALLATION DATE", validators=[DataRequired()], render_kw={"placeholder":"dd-mm-yyyy", "class":"form-control"})
    datacenter = QuerySelectField('RACK LOCATION :', allow_blank=True, query_factory=lambda: Datacenter.query.all(), get_label="dc_name")
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    r_notes = CKEditorField('NOTES :', render_kw={'class': 'form-control', 'rows': 5})
    submit = SubmitField('SAVE')

    def validate_rack(self, field):
        rackRef = Rack.query.filter_by(r_name=field.data).first()
        if rackRef and self.r_name.data != self.origin_rack.data:
            raise ValidationError('Rack Name is already in use!')

class PlatformForm(FlaskForm):
    """
    PLATFORM FORM
    """
    platform_name = StringField('DEVICE NAME :', validators=[DataRequired()])
    serial_number = StringField('SERIAL NUMBER :',validators=[DataRequired()])
    supplier = QuerySelectField('SUPPLIER :', allow_blank=True, query_factory=lambda: Supplier.query.all(), get_label="company_name")
    device_role =  QuerySelectField('DEVICE ROLE TYPE :',validators=[DataRequired()], allow_blank=True, query_factory=lambda: Device_Role.query.all(), get_label="name")
    power_supply = IntegerField('POWER SUPPLY :', default=0) 
    rack = QuerySelectField('RACK :', allow_blank=True, query_factory=lambda: Rack.query.all(), get_label="r_name", render_kw={"id": "rack_input"})
    u_hight = HiddenField()
    u_position = StringField('POSITION OF U IN RACK :',validators =[validate_u_position], render_kw={"placeholder": "from-to (example: 5-10)"})
    production_date = DateField("COMMISSIONING DATE :", validators=[DataRequired()] ,render_kw={"placeholder": "dd-mm-yyyy"})
    end_warranty_date = DateField("END WARRANTY DATE :", validators=[DataRequired()] , render_kw={"placeholder": "dd-mm-yyyy"})
    network_identity = StringField('NETWORK IDENTITY (IP/MAC) :')
    contract = QuerySelectField('MAINTENANCE CONTRACT  :', allow_blank=True, query_factory=lambda: Contract.query.all(), get_label=get_contract_info_label)
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    notes = CKEditorField('NOTES :', render_kw={'class': 'form-control', 'rows': 5})
    submit = SubmitField('SAVE')

class PlatformRackForm(FlaskForm):
    """
    PLATFORM FORM
    """
    platform_name = StringField('DEVICE NAME :', validators=[DataRequired()])
    serial_number = StringField('SERIAL NUMBER :',validators=[DataRequired()])
    supplier = QuerySelectField('SUPPLIER :', allow_blank=True, query_factory=lambda: Supplier.query.all(), get_label="company_name")
    device_role =  QuerySelectField('DEVICE ROLE TYPE :',validators=[DataRequired()], allow_blank=True, query_factory=lambda: Device_Role.query.all(), get_label="name")
    power_supply = IntegerField('POWER SUPPLY :', default=0) 
    rack = HiddenField()
    u_hight = HiddenField()
    u_position = StringField('POSITION OF U IN RACK :',validators =[validate_u_position], render_kw={"placeholder": "from-to (example: 5-10)"})
    production_date = DateField("COMMISSIONING DATE :", validators=[DataRequired()] ,render_kw={"placeholder": "dd-mm-yyyy"})
    end_warranty_date = DateField("END WARRANTY DATE :", validators=[DataRequired()] , render_kw={"placeholder": "dd-mm-yyyy"})
    network_identity = StringField('NETWORK IDENTITY (IP/MAC) :')
    contract = QuerySelectField('MAINTENANCE CONTRACT  :', allow_blank=True, query_factory=lambda: Contract.query.all(), get_label=get_contract_info_label)
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    notes = CKEditorField('NOTES :', render_kw={'class': 'form-control', 'rows': 5})
    submit = SubmitField('SAVE')

class NetworkForm(FlaskForm):
    """
    NETWORK FORM
    """
    origin_tag = HiddenField()
    origin_gatway = HiddenField()

    net_name = StringField('NETWORK NAME :', validators=[DataRequired()])
    tag = IntegerField('NETWORK TAG :',validators=[InputRequired()], render_kw={"placeholder": "Ex : 552"})
    gatway = StringField('GATWAY :', validators=[DataRequired(), IPAddress()])
    mask = StringField("NETWORK MASK :", validators=[DataRequired(), NetMask], render_kw={"placeholder": "Ex : 255.255.255.0"})
    net_notes = TextAreaField('NOTES :', render_kw={'class': 'form-control', 'rows': 5})
    datacenter = QuerySelectField('NETWORK LOCATION :', allow_blank=True, query_factory=lambda: Datacenter.query.all(), get_label="dc_name")
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    submit = SubmitField('SAVE')

    def validate_gatway(self, field):
        netGatway = Network.query.filter_by(gatway=field.data).first()
        if netGatway and self.gatway.data != self.origin_gatway.data:
            raise ValidationError('This GATWAY is already in use!')

    def validate_tag(self, field):
        netTag = Network.query.filter_by(tag=field.data).first()
        if netTag and self.tag.data != self.origin_tag.data:
            raise ValidationError('This TAG is already in use!')

class ServerForm(FlaskForm):
    """
    SERVER FORM
    """
    origin_ip = HiddenField()
    server_name = StringField('SERVER NAME :', validators=[DataRequired()])
    operating_system = SelectField('Operating System TYPE :',validators=[DataRequired()],render_kw={"class":"form-control"} , choices =[
        ('LINUX','LINUX'),
        ('UNIX','UNIX'),
        ('WINDOWS','WINDOWS'),
        ('OTHER','OTHER')])
    os_version = StringField('OS VERSION  :',validators=[DataRequired()], render_kw={"placeholder": "Ex : REDHAT 8.5 , AIX 6, 2016 SERVER "},)
    type = SelectField("TYPE  :", validators=[DataRequired()], choices =[
        ('PHYS','PHYSICAL MACHINE (PM)'),
        ('VM','VIRTUAL MACHINE (VM)'),
        ('POD','CONTAINER (POD)'),
        ('VIP','VIRTUAL IP (VIP)'),
        ('OTHER','OTHER')])
    vitality_classification= SelectField('VITALITY CLASSIFICATION :',validators=[DataRequired()],  choices =[
        ('VITAL','VITAL'),
        ('IMPORTANT','IMPORTANT'),
        ('MIDDLE','MIDDLE'),
        ('OTHER','OTHER')])
    ip_address = StringField('IP :', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message=None)])
    network = QuerySelectField('IS PART OF NETWORK :',query_factory=lambda: Network.query.all(), get_label=get_net_name_tag_label)
    platform = QuerySelectField('IS PART OF DEVICE :', allow_blank=True, query_factory=lambda: Platform.query.all(), get_label="platform_name")
    department = QuerySelectField('INTERNAL OWNER :', allow_blank=True, query_factory=lambda: Department.query.all(), get_label="name")
    project = QuerySelectField('IS PART OF PROJECT  :', allow_blank=True, query_factory=lambda: Project.query.all(), get_label="project_name")
    notes = CKEditorField('NOTES :', render_kw={'class': 'form-control', 'rows': 5})
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    
    applications_list = StringField('APPLICATIONS : ', render_kw = {"class":"form-control",  "id":"apps_name"})

    submit = SubmitField('SAVE')

    def validate_ip_address(self, field):
        ipAddress = Server.query.filter_by(ip_address=field.data).first()
        if ipAddress and self.ip_address.data != self.origin_ip.data:
            raise ValidationError('IP Address is already in use!')

    def validate_ip_address(self, field):
        if not check_ip_in_network_by_id((self.network.data).id, field.data):
            raise ValidationError('IP Address is not in range of this Networks.')

class ServerNetworkForm(FlaskForm):
    """
    SERVER FORM
    """
    origin_ip = HiddenField()
    server_name = StringField('SERVER NAME :', validators=[DataRequired()])
    operating_system = SelectField('Operating System TYPE :',validators=[DataRequired()],render_kw={"class":"form-control"} , choices =[
        ('LINUX','LINUX'),
        ('UNIX','UNIX'),
        ('WINDOWS','WINDOWS'),
        ('OTHER','OTHER')])
    os_version = StringField('OS VERSION  :',validators=[DataRequired()], render_kw={"placeholder": "Ex : REDHAT 8.5 , AIX 6, 2016 SERVER "},)
    type = SelectField("TYPE  :", validators=[DataRequired()], choices =[
        ('PHYS','PHYSICAL SERVER'),
        ('VM','VIRTUAL MACHINE (VM)'),
        ('POD','CONTAINER (POD)'),
        ('VIP','VIRTUAL IP (VIP)'),
        ('OTHER','OTHER')])
    vitality_classification= SelectField('VITALITY CLASSIFICATION :',validators=[DataRequired()],  choices =[
        ('VITAL','VITAL'),
        ('IMPORTANT','IMPORTANT'),
        ('MIDDLE','MIDDLE'),
        ('OTHER','OTHER')])
    ip_address = StringField('IP ADDRESS :', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message=None)])
    network = HiddenField("My Network selection")
    platform = QuerySelectField('IS PART OF DEVICE :', allow_blank=True, query_factory=lambda: Platform.query.all(), get_label="platform_name")
    department = QuerySelectField('INTERNAL OWNER DEPARTEMENT :', allow_blank=True, query_factory=lambda: Department.query.all(), get_label="name")
    project = QuerySelectField('IS PART OF PROJECT  :', allow_blank=True, query_factory=lambda: Project.query.all(), get_label="project_name")
    notes = CKEditorField('NOTES :', render_kw={'class': 'form-control', 'rows': 5})
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    
    applications_list = StringField('APPLICATIONS : ', render_kw = {"class":"form-control",  "id":"apps_name"})

    submit = SubmitField('SAVE')

    def validate_ip_address(self, field):
        ipAddress = Server.query.filter_by(ip_address=field.data).first()
        if ipAddress and self.ip_address.data != self.origin_ip.data:
            raise ValidationError('IP Address is already in use!')

class VulnerabilityForm(FlaskForm):
    """
    VULNERABILITY FORM
    """
    title_vulnerability = StringField('VULNERABILITY NAME :', validators=[DataRequired()])
    date_vulnerability = DateField("DETECTION DATE", validators=[DataRequired()], render_kw={"placeholder": "dd-mm-yyyy"})
    cvs_code = StringField("CVE-ID CODES :", validators=[DataRequired()])
    severity = SelectField('SEVERITY LEVEL:', choices =[
        ("INFORMATION","INFORMATION"),
        ("LOW","LOW"),
        ("MEDIUM","MEDIUM"),
        ("HIGH","HIGH"),
        ("CRITICAL","CRITICAL")])
    risk = SelectField('RISK LEVEL :', choices =[
        ("ACCEPTABLE","ACCEPTABLE"),
        ("TOLERABLE","TOLERABLE"),
        ("UNDESIRABLE","UNDESIRABLE"),
        ("INTOLERABLE","INTOLERABLE")])
    impact = CKEditorField('IMPACT NOTES:', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 8})
    ticket = QuerySelectField('TICKET ID :',allow_blank=True, query_factory=lambda: Ticket.query.all(), get_label="ticket_number")
    admin = QuerySelectField('SUPPORTED BY :',allow_blank=True,query_factory=lambda: Admin.query.all(), get_label=get_admin_complet_name_label)
    recommanded_solution = CKEditorField('RECOMMANDATIONS :', render_kw={'class': 'form-control', 'rows': 5})
    
    submit = SubmitField('SAVE')

class ProjectForm(FlaskForm):
    """
    PROJECT FORMULAIRE
    """
    project_name = StringField('PROJECT NAME :', validators=[DataRequired()])
    description = CKEditorField('PROJCET DESCRIPTION :', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 5})
    admin = QuerySelectField('RESPONSABL NAME :',query_factory=lambda: Admin.query.all(), get_label=get_admin_complet_name_label)
    affectation_date = DateField('AFFECTATION DATE  :', validators=[DataRequired()], render_kw={"placeholder": "dd-mm-yyyy"})
    members = StringField('PROJECT INTERNAL MEMBERS NAME :', render_kw= {"class":"form-control", "id":"members"})
    external_members = StringField('PROJECT EXTERNAL MEMBERS NAME :', render_kw= {"class":"form-control", "id":"external_members"})
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    status = SelectField('PROJECT STATUT :', choices =[
        ('PROGRESS','IN PROGRESS'),
        ('HOLD','ON HOLD'),
        ('COMPLETE','COMPLETE')])
    complete_date = HiddenField(render_kw={"placeholder": "01-12-2020"})
    submit = SubmitField('SAVE')

class ProjectDocumentsForm(FlaskForm):
    """
    PROJECT DOCUMENTS FORMULAIRE
    """
    document_name = FileField('UPLOADE DOCUMENT :', validators=[DataRequired()])
    description = StringField('DOCUMENT DESCRIPTION :', validators=[DataRequired()], render_kw={'class': 'form-control'})
    submit = SubmitField('SAVE')

    def validate_document_name(self, field):
        if ProjectDocuments.query.filter_by(document_name=field.data.filename).first():
            raise ValidationError('Document Name is already existe!')

    def validate_document_name(self, field):
        filename = field.data.filename
        if not ('.' in filename and filename.rsplit('.', 1)[1].lower()  in current_app.config['ALLOWED_EXTENSIONS']):
            raise ValidationError('Invalide Document Extention, Allowed Extention (pdf, doc, docx, xls, xlsx ) !')

class ContractForm(FlaskForm):
    """
    CONTRACT FORMULAIRE
    """
    contract_number = StringField('CONTRACT NUMBER :', validators=[DataRequired()])
    start_date = DateField('START DATE  :', validators=[DataRequired()], render_kw={"placeholder": "dd-mm-yyyy"})
    end_date = DateField('END DATE  :', validators=[DataRequired()], render_kw={"placeholder": "dd-mm-yyyy"})
    contract_document = FileField('UPLOADE CONTRACT DOCUMENT :')
    notes = CKEditorField('CONTRACT NOTES :', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 5})
    supplier = QuerySelectField('SUPPLIER NAME :', allow_blank=True, query_factory=lambda: Supplier.query.all(), get_label="company_name")
    submit = SubmitField('SAVE')

    def validate_contract_document(self, field):
        if field.data.filename != "":
            filename = field.data.filename
            if not ('.' in filename and filename.rsplit('.', 1)[1].lower()  in current_app.config['ALLOWED_EXTENSIONS']):
                raise ValidationError('Invalide Document Extention, Allowed Extention (pdf, doc, docx, xls, xlsx ) !')
        else :
            pass

class ApplicationForm(FlaskForm):
    """
    APPLICATIONS FORMULAIRE
    """
    app_name  = StringField('APPLICATION NAME :', validators=[DataRequired()])
    app_version  = StringField('APPLICATION VERSION  :', validators=[DataRequired()], render_kw={"placeholder": "Ex : 2.0.12"})
    app_description  = TextAreaField('DESCRIPTION  :', validators=[DataRequired()])
    app_ports  = StringField('USERD PORT(S) :', render_kw={"placeholder": "Ex: 80, 991, 6676"})
    tags = StringField('TAGS :', render_kw= {"class":"form-control", "id":"tags"})
    submit = SubmitField('SAVE')

class DeviceRoleForm(FlaskForm):
    """
    Device Role FORMULAIRE
    """
    name = StringField('NAME :',validators=[DataRequired()])
    description = StringField(' DESCRIPTION :', validators=[DataRequired()], render_kw={"placeholder": "Describe your Device role"})
    device_color = StringField(' COLOR :', validators=[DataRequired()], render_kw={"type": "color"})
    submit = SubmitField('SAVE')

class ImportCSVForm(FlaskForm):
    import_data = FileField("IMPORT CSV File : ")
    text_data = TextAreaField("""IMPORT DATA : """, render_kw={'class': 'form-control', 'rows': 20,  'placeholder' : "Enter the list of column headers followed by one line per record to be imported, using semicolon (;) to separate values."})    
    submit = SubmitField('SUBMIT TO DB')

class SMTPConfigForm(FlaskForm):
    """
    SMTP CONFIG FORMULAIRE
    """
    egroup_vulnerability = TextAreaField('SEND NOTIFICATION OF VULNERABILITIES TO USERS:', render_kw={'class': 'form-control', 'rows': 5, "placeholder": "email1@server.com, email2@server.com, email3@server.com"})
    egroup_ticket = TextAreaField('SEND NOTIFICATION OF TICKETS TO USERS:', render_kw={'class': 'form-control', 'rows': 5,  "placeholder": "email1@server.com, email2@server.com, email3@server.com"})
    egroup_contract = TextAreaField('SEND NOTIFICATION OF CONTRACTS TO USERS:', render_kw={'class': 'form-control', 'rows': 5,  "placeholder": "email1@server.com, email2@server.com, email3@server.com"})
    submit = SubmitField('SAVE')