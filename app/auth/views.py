#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Author: Abdellah ALAOUI ISMAILI
#   
#  Project Name: InfraLinker
#  Project web Site: https://infralinker.net
"""
This view auth file containing the auth view functions for InfraLinker App, routes and the map to navigate in app.
"""

from flask import flash, redirect,abort, render_template, url_for, request, g, current_app,Flask, session, app
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime, time, date, timedelta
import datetime
from . import auth
from .forms import LoginForm, SupplierForm,TagForm, ContactForm, EditEndUserForm, ResetPasswordForm,InterventionForm, Add_Note_vunerability, TicketForm, ActionForm
from .. import db, login_manager
from ..models import Admin, Supplier,Tag, Ticket, Platform, Vulnerability, Intervention, Project, Action, Contact, Select2MultipleField, Emailling_config, Contract
from config import app_config
import schedule
import time
from threading import Thread
from sqlalchemy import text
import pandas as pd
import pandas.io.sql as psql
from ..library.emailling import change_log , send_email
from ..library.querys import query_list_actions_for_project, query_count_ticket_status_by_supplier_id
from ..library.ip_calculator import check_expiration_date
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import plotly
    

def get_UserName(id):
    first_name = db.session.query(Admin.firstname).filter(Admin.id == id).scalar()
    last_name = db.session.query(Admin.lastname).filter(Admin.id == id).scalar()
    return first_name, last_name


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

def check_request_to_change_password():
    if current_user.change_password is True:
        return redirect(url_for('auth.password_resetter', id=current_user.id))
        current_user.change_password.set(False)

@auth.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    session.modified = True
    g.user = current_user

@auth.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.now() #utcnow doesn't actually attach a timezone
        db.session.add(current_user) 
        db.session.commit()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle requests to the /login route
    Log an admine in through the login form
    """

    if current_user.is_authenticated:
        make_session_permanent()
        flash('You are already logged in.', "info")
        return redirect(url_for('home.homepage'))

    form = LoginForm()
    if form.validate_on_submit():

        admine = Admin.query.filter_by(email=form.email.data).first()

        if admine is not None and admine.verify_password(
                form.password.data):

            login_user(admine)
            
            if admine.change_password:
                return redirect(url_for('auth.password_resetter', id=admine.id))

            return redirect(url_for('home.admin_dashboard')) 


        # when login details are incorrect
        else:
            flash('Invalid email or password.' , 'danger')

    # load login template
    return render_template('auth/login.html', form=form, title='LOGIN TO YOUR ACCOUNT')

@auth.route('/logout')
@login_required
def logout():
    """
    Handle requests to the /logout route
    Log an admine out through the logout link
    """
    logout_user()
    flash('You have successfully been logged out.', 'success')

    # redirect to the login page
    return redirect(url_for('auth.login'))

###########################################################
### PROFIL & PASSWORD MANAGEMENT MODUL                #####
###########################################################
@auth.route('/admins/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_end_user(id):
    """
    Edit a admin
    """
    new_admin = False

    admin = Admin.query.get_or_404(id)

    if admin != current_user:
        abort(403)

    form = EditEndUserForm(obj=admin)
    if form.validate_on_submit():

        admin.firstname = form.firstname.data.capitalize()
        admin.lastname = form.lastname.data.upper()
        admin.email = form.email.data
        admin.phone = form.phone.data
        admin.function = form.function.data


        db.session.commit()
        flash('Saved successfully.', 'success')

        # redirect to the admins page
        return redirect(url_for('home.user_dashboard'))

    form.firstname.data = admin.firstname
    form.lastname.data = admin.lastname
    form.email.data = admin.email
    form.phone.data = admin.phone
    form.function.data = admin.function

    return render_template('admin/users/register_new_admin.html', action="Edit",
                           new_admin=new_admin, form=form,
                           admin=admin, title="Edit Admin")

@auth.route('/change_your_password/admin/<int:id>', methods=['GET','POST'])
# @login_required
def password_resetter(id):

    user_change = Admin.query.get_or_404(id)

    if user_change != current_user:
        abort(403)
    form = ResetPasswordForm(obj=user_change)

    if form.validate_on_submit():
        user_change.password = form.new_password.data
        user_change.change_password = False
        db.session.add(user_change)
        db.session.commit()
        flash('Password changed successfully!', 'success')

        return redirect(url_for('home.user_dashboard'))

    return render_template('admin/users/change_password.html',
                form=form, title=('Reset your password'))

#######################################
### SUPPLIERS MANAGEMENT MODULES ######
#######################################

@auth.route('/suppliers', methods=['GET', 'POST'])

@login_required
def suppliers_list():
    """
    List all suppliers
    """
    suppliers = Supplier.query.all()
    contacts = Contact.query.all()
    return render_template('auth/suppliers/suppliers.html',
                           suppliers=suppliers,
                           contacts=contacts,
                           title="SUPPLIERS LIST")

@auth.route('/supplier/add', methods=['GET', 'POST'])
@login_required
def new_supplier():
    """
    Add a supplier to the database
    """
    new_supplier = True
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(company_name=form.company_name.data.upper(),
                                address = form.address.data,
                                city = form.city.data,
                                phone = form.phone.data,
                                add_by = current_user.id,
                                add_date = datetime.datetime.now(),
                                notes = form.notes.data)

        try:
            # add supplier to the database
            db.session.add(supplier)
            db.session.commit()
            flash('You have successfully added a new supplier.', 'success')
            change_log('Supplier', 'New', supplier.id, supplier.company_name)
        except:
            # in case supplier name already exists
            flash('Error: supplier name already exists.')

        # redirect to suppliers page
        return redirect(url_for('auth.suppliers_list'))

    # load department template
    return render_template('auth/suppliers/supplier.html', action="Add",
                           new_supplier=new_supplier, form=form,
                           title="ADD NEW SUPPLIER")

@auth.route('/supplier/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    """
    Edit a supplier
    """
    new_supplier = False

    supplier = Supplier.query.get_or_404(id)
    form = SupplierForm(obj=supplier)

    if current_user.id != supplier.add_by and not current_user.is_admin:
        abort(403)

    if form.validate_on_submit():

        supplier.company_name = form.company_name.data.upper()
        supplier.address = form.address.data
        supplier.city = form.city.data
        supplier.phone = form.phone.data
        supplier.notes = form.notes.data


        db.session.commit()
        flash('Edited Supplier Saved successfully.', 'success')
        change_log('Supplier', 'Edit', supplier.id, supplier.company_name)

        # redirect to the suppliers page
        return redirect(url_for('auth.suppliers_list'))

    form.company_name.data = supplier.company_name
    form.address.data = supplier.address
    form.city.data = supplier.city
    form.phone.data = supplier.phone
    form.notes.data = supplier.notes


    return render_template('auth/suppliers/supplier.html', action="Edit",
                           new_supplier=new_supplier, form=form,
                           supplier=supplier, title="Edit Supplier")

# Function to check if there are dependencies for Multible Model
def check_supplier_dependencies(supplier_id):
    dependent_models = [Platform, Contract, Contact, Ticket]
    for model in dependent_models:
        if model.query.filter_by(supplier_id=supplier_id).first() is not None:
            return True
    return False

@auth.route('/supplier/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_supplier(id):
    """
    Delete a supplier from the database
    """
    supplier = Supplier.query.get_or_404(id)

    if current_user.id != supplier.add_by and not current_user.is_admin:
        abort(403)

    if check_supplier_dependencies(id) :
        flash("Cannot delete this supplier with dependencies in Devices, Contracts, Contacts, or Tickets. Please check before Deleting.", 'error')
        return redirect(url_for('auth.suppliers_list'))
        
    # check_admin()

    
    change_log('Supplier', 'Delete', supplier.id, supplier.company_name)
    db.session.delete(supplier)
    db.session.commit()
    flash('Deleted successfully.', 'warning')

    # redirect to the departments page
    return redirect(url_for('auth.suppliers_list'))

    

@auth.route('/details/supplier/<int:id>', methods=['GET'])

@login_required
def supplier_details(id):
    """
    Show supplier Details
    """
    supplier = Supplier.query.get_or_404(id)
    devices = Platform.query.filter_by(supplier_id = id).all()
    contracts = Contract.query.filter_by(supplier_id = id).all()
    tickets = Ticket.query.filter_by(supplier_id = id).all()
    contacts = Contact.query.filter_by(supplier_id = id).all()

    colors=["#E8505B","#14B1AB","#F9D56E","#F3ECC2"]
    labels_count_ticket_status_by_supplier_id = query_count_ticket_status_by_supplier_id(id)["status"]
    values_count_ticket_status_by_supplier_id = query_count_ticket_status_by_supplier_id(id)["count_tickets"]
    figTicketBySupplierID = go.Figure(data=[go.Pie(labels=labels_count_ticket_status_by_supplier_id, 
    hole =.5, marker=dict(colors=colors, line=dict(color='#FFFFFF', width=10)),
    values=values_count_ticket_status_by_supplier_id, title = '')])
    
    figTicketBySupplierID.update_layout(margin={'t':2,'l':0,'b':0,'r':0})
    figTicketBySupplierID.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

    graphSunBurt_Tickes_by_Supplier_id = json.dumps(figTicketBySupplierID, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('auth/suppliers/supplier_details.html', supplier=supplier,get_UserName=get_UserName,
    devices=devices,contracts=contracts,tickets=tickets,contacts=contacts,check_expiration_date=check_expiration_date, 
    graphSunBurt_Tickes_by_Supplier_id=graphSunBurt_Tickes_by_Supplier_id, title="SHOW SUPPLIER DETAILS")

###################################
###CONTACT MANAGEMENT MODULE ######
################################### 

@auth.route('/contacts/<int:supplier_id>', methods=['GET', 'POST'])

@login_required
def list_contacts(supplier_id):
    """
    List all contacts
    """
    
    contacts = Contact.query.filter_by(supplier_id =supplier_id).all()
    return render_template('auth/contacts/contacts.html',
                           contacts = contacts,
                           title="LISTE OF CONTACTS")

@auth.route('/contact/add', methods=['GET', 'POST'])
@login_required
def new_contact():
    """
    Add a contact to the database
    """

    new_contact = True

    form = ContactForm()

    if form.validate_on_submit():
        contact = Contact(
                    firstname=form.firstname.data.capitalize(),
                    lastname = form.lastname.data.upper(),
                    supplier = form.supplier.data,
                    email = form.email.data,
                    phone = form.phone.data,
                    notes = form.notes.data)

        # add contact to the database
        db.session.add(contact)
        db.session.commit()
        change_log("Contact","New" , contact.id, contact.firstname +" "+ contact.lastname)
        
        flash('You have successfully added a new contact.', 'success')

        # redirect to contacts page
        return redirect(url_for('auth.suppliers_list'))

    # load department template
    return render_template('auth/contacts/contact.html', action="Add",
                           form=form, new_contact=new_contact,
                           title="ADD NEW CONTACT")

@auth.route('/contacts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    """
    Edit a contact
    """
  

    new_contact = False

    contact = Contact.query.get_or_404(id)
    form = ContactForm(obj=contact)
    if form.validate_on_submit():

        contact.firstname = form.firstname.data.capitalize() 
        contact.lastname = form.lastname.data.upper()
        contact.supplier = form.supplier.data
        contact.email = form.email.data
        contact.phone = form.phone.data
        contact.notes = form.notes.data


        db.session.commit()
        change_log("Contact","Edit" , contact.id, contact.firstname +" "+ contact.lastname)
        flash('Edited Contact Saved successfully.', 'success')

        # redirect to the fournisseurs page
        # return redirect(url_for('auth.list_contacts'))
        return redirect(url_for('auth.suppliers_list'))

    form.firstname.data = contact.firstname
    form.lastname.data = contact.lastname
    form.supplier.data = contact.supplier
    form.email.data = contact.email
    form.phone.data = contact.phone
    form.notes.data = contact.notes

    return render_template('auth/contacts/contact.html', action="Edit",
                           new_contact=new_contact, form=form,
                           contact=contact, title="Edit contact")

@auth.route('/contacts/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_contact(id):
    """
    Delete a contact from the database
    """
    
    contact = Contact.query.get_or_404(id)
    change_log("Contact","Delete" , contact.id, contact.firstname +" "+ contact.lastname)

    db.session.delete(contact)
    db.session.commit()
    flash('Deleted successfully.', 'warning')

    # redirect to the departments page
    return redirect(url_for('auth.suppliers_list'))

    

################################################
###ADD NOTES TO VULNERABILITY ####
################################################

@auth.route('/vulnerability/observation/<int:id>', methods=['GET', 'POST'])
@login_required
def add_observation(id):
    """
    Add new observation
    """
    vulnerability = Vulnerability.query.get_or_404(id)
    form = Add_Note_vunerability(obj=vulnerability)

    if vulnerability.admin_id != current_user.id and not current_user.is_admin :
        abort(403)

    if not vulnerability:
        flash('Error: invalid vulnerability')
        abort(404)

    new_vulnerability = False

    if form.validate_on_submit():

        vulnerability.vulnerabitlity_note = form.vulnerabitlity_note.data.capitalize() 
        db.session.commit()
        flash('Saved successfully.', 'success')

        return redirect(url_for('admin.list_vulnerabilities'))

    form.vulnerabitlity_note.data = vulnerability.vulnerabitlity_note

    return render_template('admin/vulnerabilities/observation.html', vulnerability=vulnerability,
                           form=form, title="vulnerability Observation")

##################################################
###### TICKETS MANAGEMENT MODULE #########
##################################################

@auth.route('/tickets', methods=['GET', 'POST'])
@login_required
def list_tickets():
    """
    List all tickets
    """
    from sqlalchemy import case

    # Assuming `status` is the column with the ticket status,
    # and `open_date` is the column with the date the ticket was opened.
    priority_order = case(
        {'OPEN': 0, 'RESOLVED': 1, 'CANCELED': 2},
        value=Ticket.status,
        else_=3
    )

    tickets = Ticket.query.order_by(priority_order).order_by(Ticket.open_date.desc()).all() 

    return render_template('auth/tickets/tickets.html',
                           tickets=tickets,
                           title="LIST ALL TICKETS")

@auth.route('/ticket/add', methods=['GET', 'POST'])
@login_required
def new_ticket():
    """
    Add an ticket to the database through the tickets user form
    """
    new_ticket = True
    emailling_details = Emailling_config.query.get_or_404(1)

    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
        ticket_number = form.ticket_number.data.upper(),
        open_date = form.open_date.data,
        description = form.description.data.capitalize(),
        supplier = form.supplier.data,
        platform = form.platform.data,
        admin_id = current_user.id,
        priority = form.priority.data,
        impact = form.impact.data,
        status = form.status.data,
        resolution_date = form.resolution_date.data,
        add_by = current_user.id,
        add_date = datetime.datetime.now(),
        comments = form.comments.data.capitalize())
        
        try:

            db.session.add(ticket)
            db.session.commit()
            flash('New ticket added successfully!', 'success')
            change_log("Ticket","New" , ticket.id, ticket.ticket_number)
            
            #FUNCTION TO SEND EMAIL TO GROUPE FOR NEW TICKET
            emails_group = emailling_details.egroup_ticket

            if emails_group :

                recipients = [email.strip() for email in emails_group.strip('()').split(',')]
                send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
                subject = (""" [DCIM] - NEW TICKET HAVE BEEN OPENED """)
                html_template = render_template('email/email-ticket.html', ticket=ticket, send_time=send_time)
                send_email(recipients, subject, html_template)
            else :
                pass
        
        except Exception as e:
            flash('Failed to Save to DataBase: '+ str(e), 'danger')
        
        #Redirection to Tickets Lists.
        return redirect(url_for('auth.list_tickets'))

    # load registration template
    return render_template('auth/tickets/ticket.html', new_ticket=new_ticket, form=form, title='Nouvelle Ticket')

@auth.route('/tickets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(id):
    """
    Edit a ticket
    """

    new_ticket = False

    ticket = Ticket.query.get_or_404(id)
    emailling_details = Emailling_config.query.get_or_404(1)

    form = TicketForm(obj=ticket)
    form.origin_ticket_number.data = ticket.ticket_number
    if form.validate_on_submit():

        ticket.ticket_number  = form.ticket_number.data.upper()
        ticket.open_date  = form.open_date.data
        ticket.description  = form.description.data.capitalize()
        ticket.supplier  = form.supplier.data        
        ticket.platform = form.platform.data
        ticket.priority = form.priority.data
        ticket.impact = form.impact.data
        ticket.status = form.status.data
        ticket.resolution_date = datetime.datetime.now() if ticket.status == "RESOLVED" else "0000-00-00" #form.resolution_date.data
        ticket.comments = form.comments.data.capitalize() 

        #SEND EMAIL IF TICKET IS RESOLVED
        emails_group = emailling_details.egroup_ticket
        send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

        if ticket.status == "RESOLVED" and  emails_group :

            recipients = [email.strip() for email in emails_group.strip('()').split(',')]
            subject = "[INFRALINKER] - RESOLUTION CONFIRMED FOR THE TICKET " + ticket.ticket_number
            html = render_template('email/email-ticket.html', ticket=ticket, send_time=send_time)
            send_email(recipients, subject, html)
                
            flash('TICKET : '+ ticket.ticket_number +' RESOLVED.')

        else :

            flash('Edited Ticket Saved successfully.', 'success')
        
        db.session.commit()
        change_log("Ticket","Edit" , ticket.id, ticket.ticket_number)
        return redirect(url_for('auth.list_tickets'))

    form.ticket_number = ticket.ticket_number
    form.open_date = ticket.open_date
    form.description = ticket.description
    form.supplier = ticket.supplier
    form.platform = ticket.platform
    form.priority = ticket.priority
    form.impact = ticket.impact
    form.status = ticket.status
    form.comments = ticket.comments

    return render_template('auth/tickets/ticket.html', action="Edit",
                           new_ticket=new_ticket, form=form,
                           ticket=ticket, title="Edit Tickets")

# Function to check if there are dependencies for Multible Model
def check_ticket_dependencies(ticket_id):
    dependent_models = [Vulnerability, Intervention]
    for model in dependent_models:
        if model.query.filter_by(ticket_id=ticket_id).first() is not None:
            return True
    return False

@auth.route('/tickets/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_ticket(id):
    """
    Delete a ticket from the database
    """

    ticket = Ticket.query.get_or_404(id)
    if ticket.admin_id != current_user.id:
        abort(403)

    if check_ticket_dependencies(id) :        
        flash("Cannot delete this ticket with dependencies in Intervention or Vlnerability. Please check before Deleting.", 'error')
        return redirect(url_for('auth.list_tickets'))


    db.session.delete(ticket)
    db.session.commit()
    change_log("Ticket","Delete" , ticket.id, ticket.ticket_number)
    flash('Deleted successfully.', 'warning')

    return redirect(url_for('auth.list_tickets'))
    

@auth.route('/tickets_repport/status_<string:ticket_status>', methods=['GET', 'POST'])
@login_required
def tickets_repport(ticket_status):
    """
    List tickets per status
    """
    if ticket_status=="ALL":
        tickets = Ticket.query.all()
    else:
        tickets = Ticket.query.filter_by(status =ticket_status).order_by(Ticket.open_date.desc()).all()

    return render_template('auth/tickets/repports/tickets_repport.html',
                        
                        tickets=tickets,
                        ticket_status = ticket_status,
                        title="TICKETS LIST")

@auth.route('/details/ticket/<int:id>', methods=['GET'])
@login_required
def ticket_details(id):
    """
    Show ticket Details
    """
    ticket = Ticket.query.get_or_404(id)
    interventions = Intervention.query.filter_by(ticket_id = id).all()
    vulnerabilities = Vulnerability.query.filter_by(ticket_id = id).all()

    return render_template('auth/tickets/ticket_details.html', ticket=ticket,get_UserName=get_UserName,
    interventions=interventions,vulnerabilities=vulnerabilities, title="SHOW TICKET DETAILS")

############################################
###INTERVENTIONS MANAGEMENT MODULE #####
############################################
@auth.route('/ticket/<int:id_ticket>/intervention/add', methods=['GET', 'POST'])
@login_required
def new_intervention(id_ticket):
    """
    Add an intervention to the database through the project form
    """
    form = InterventionForm()
    ticket = Ticket.query.get(id_ticket)
    if not ticket:
        flash('Error: invalid ticket ID')
        abort(404)

    if form.validate_on_submit():
        intervention = Intervention(
        ticket = ticket,
        intervention_date = form.intervention_date.data,
        comment = form.comment.data.capitalize(),
        admin = form.admin.data,
        contact = form.contact.data)
        try:
            db.session.add(intervention)
            db.session.commit()

            flash('You have successfully added a new intervention.', 'success')
        except:
            flash('Error: intervention ID already exists.')

        return redirect(url_for('auth.list_tickets'))

    return render_template('auth/interventions/intervention.html',new_intervention=new_intervention, intervention="Add", form=form,
                           title="ADD NEW INTERVENTION")

@auth.route('/interventions/tickets_<int:id_ticket>', methods=['GET'])
@login_required
def list_interventions(id_ticket):
    """
    List all intervention
    """
    interventions = Intervention.query.filter_by(ticket_id =id_ticket).all()
    return render_template('auth/interventions/interventions.html',
                           interventions=interventions,
                           title="LIST ALL INTERVENTIONS")

@auth.route('/intervention/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_intervention(id):
    """
    Edit a intervention
    """

    new_intervention = False

    intervention = Intervention.query.get_or_404(id)
    form = InterventionForm(obj=intervention)
    if form.validate_on_submit():

        intervention.intervention_date = form.intervention_date.data
        intervention.comment = form.comment.data.capitalize()
        intervention.admin = form.admin.data
        intervention.contact = form.contact.data

        db.session.commit()
        flash('Task Saved successfully.', 'success')

        # redirect to the fournisseurs page
        return redirect(url_for('auth.list_tickets'))

    form.intervention_date.data = intervention.intervention_date
    form.comment.data = intervention.comment
    form.admin.data = intervention.admin
    form.contact = intervention.contact

    return render_template('auth/interventions/intervention.html',
                           new_intervention=new_intervention, form=form,
                           intervention=intervention, title="Edit intervention")

@auth.route('/intervention/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_intervention(id):
    """
    Delete a intervention from the database
    """
    ticket = Ticket.query.get(id)
    intervention = Intervention.query.get_or_404(id)
    db.session.delete(intervention)
    db.session.commit()
    flash('Deleted successfully.', 'warning')

    # redirect to the departments page
    return redirect(url_for('auth.list_interventions', id_ticket=ticket.id))

    

##########################################
### ACTION PROJECT MANAGEMENT MODULES ####
##########################################
@auth.route('/project/<int:project_id>/action/add', methods=['GET', 'POST'])
@login_required
def new_action(project_id):
    """
    Add an action to the database through the project form
    """
    project = Project.query.get(project_id)
    if not project:
        flash('Error: invalid project')
        abort(404)

    form = ActionForm()
    if form.validate_on_submit():
        action = Action(project = project,
        description = form.description.data.capitalize(),
        status = form.status.data,
        execution_date = form.execution_date.data,
        finish_date = form.finish_date.data
        )

        try:
            db.session.add(action)
            db.session.commit()
            flash('You have successfully added a new action.', 'success')
        except:
            flash('Error: Something wrong!')

        # redirect to actions page
        return redirect(url_for('auth.list_actions', project_id=project.id))

    # load department template
    return render_template('auth/actions/action.html', action="Add", form=form, new_action=new_action, project=project,
                           title="ADD NEW ACTION")

# import plotly.figure_factory as ff
@auth.route('/actions/project_<int:project_id>', methods=['GET'])

@login_required
def list_actions(project_id):
    """
    List all actions
    """
    # colors = ["darkorange", "dodgerblue","darkgreen", "red"]
    actions = Action.query.filter_by(project_id =project_id).all()
    actions_plot_gant_diag = query_list_actions_for_project(project_id)
    actions_plot_gant_diag["execution_date"] = pd.to_datetime(actions_plot_gant_diag["execution_date"])
    actions_plot_gant_diag["finish_date"] = pd.to_datetime(actions_plot_gant_diag["finish_date"])

    # display only 5 words from description texte and Add ellipsis (...) at the end of each truncated description
    actions_plot_gant_diag['description'] = actions_plot_gant_diag['description'].apply(lambda x: ' '.join(x.split()[:7]))
    actions_plot_gant_diag['description'] = actions_plot_gant_diag['description'] + '...'

    fig = px.timeline(actions_plot_gant_diag, x_start="execution_date", x_end="finish_date", y="status", color="description", color_discrete_sequence = px.colors.qualitative.Vivid)
    fig.update_layout(
                # title='PROJECT GANTT CHART',
                # bargap=0.5,
                # width=1624,
                # height=600,              
                xaxis_title="TIMES", 
                yaxis_title="TASKS STATUS",                   
                title_x=0.5, 
                legend_title="",
                # legend = dict(orientation = 'v', xanchor = "left", x=0 , yanchor="bottom",  y=-0.6), #Adjust legend position
            )
    fig.update_yaxes(autorange = "reversed") 
    fig.update_xaxes(tickangle=-7,side ="top",  tickfont=dict(family='Arial', color='darkgray', size=14))
    
    graphChart_For_Actions = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('auth/actions/actions.html',
                           actions=actions,
                           project_id=project_id,
                           graphChart_For_Actions=graphChart_For_Actions, 
                           title="LIST ALL ACTIONS")

@auth.route('/action/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_action(id):
    """
    Edit a action
    """


    new_action = False

    action = Action.query.get_or_404(id)
    form = ActionForm(obj=action)
    if form.validate_on_submit():

        action.description = form.description.data.capitalize()
        action.status = form.status.data
        action.execution_date = form.execution_date.data
        action.finish_date = form.finish_date.data

        db.session.commit()
        flash('Action Saved successfully.', 'success')

        # redirect to the fournisseurs page
        return redirect(url_for('auth.list_actions', project_id=action.project_id))


    form.description.data = action.description
    form.status.data = action.status
    form.execution_date = action.execution_date
    form.finish_date = action.finish_date

    return render_template('auth/actions/action.html',
                           new_action=new_action, form=form,
                           action=action, title="Edit action")

@auth.route('/action/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_action(id):
    """
    Delete a action from the database
    """
  

    action = Action.query.get_or_404(id)
    db.session.delete(action)
    db.session.commit()
    flash('Deleted successfully.', 'warning')

    # redirect to the departments page
    return redirect(url_for('auth.list_actions', project_id=action.project_id))

###################################
###TAGS MANAGEMENT MODULE ######
################################### 

@auth.route('/tags', methods=['GET', 'POST'])

@login_required
def tags_list():
    """
    List all tags
    """
    tags = Tag.query.all()
    return render_template('auth/tags/tags.html', get_UserName=get_UserName,
                           tags=tags, title="TAGS LISTE")

@auth.route('/tag/add', methods=['GET', 'POST'])
@login_required
def new_tag():
    """
    Add new tag to the database
    """
    new_tag = True
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(
            tag_name=form.tag_name.data.upper(),
            tag_description = form.tag_description.data.upper(),
            tag_color = form.tag_color.data,
            add_by = current_user.id,
            add_date = datetime.datetime.now()
            )

        try:
            db.session.add(tag)
            db.session.commit()
            flash('You have successfully added a new tag.', 'success')
            change_log('Tag', 'New', tag.id, tag.tag_name)
        except:
            # in case tag name already exists
            flash('Error: tag name already exists.')

        # redirect to tags page
        return redirect(url_for('auth.tags_list'))

    # load department template
    return render_template('auth/tags/tag.html', action="Add",
                           new_tag=new_tag, form=form,
                           title="ADD NEW TAG")

@auth.route('/tag/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tag(id):
    """
    Edit a tag
    """
    new_tag = False
    tag = Tag.query.get_or_404(id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():

        tag.tag_name = form.tag_name.data.upper()
        tag.tag_description = form.tag_description.data.upper()
        tag.tag_color = form.tag_color.data

        db.session.commit()
        flash('Tag Saved successfully.', 'success')
        change_log('Tag', 'Edit', tag.id, tag.tag_name)
        return redirect(url_for('auth.tags_list'))

    form.tag_name.data = tag.tag_name
    form.tag_description.data = tag.tag_description
    form.tag_color.data = tag.tag_color

    return render_template('auth/tags/tag.html', action="Edit",
                           new_tag=new_tag, form=form,
                           tag=tag, title="Edit TAG")

@auth.route('/tag/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tag(id):
    """
    Delete a tag from the database
    """
    check_admin()
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Deleted successfully.', 'warning')
    change_log('Tag', 'Delete', tag.id, tag.tag_name)

    # redirect to the departments page
    return redirect(url_for('auth.tags_list'))