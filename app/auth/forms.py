#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Author: Abdellah ALAOUI ISMAILI
#   
#  Company Name: InfraLinker
#  Company web Site: http://infralinker.net
"""
Auth Form
"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, BooleanField, SelectField, TextAreaField, DateTimeField, HiddenField,SelectMultipleField, DateField
from datetime import datetime
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import widgets
from ..models import Admin, Supplier, Ticket, Platform, Vulnerability, Intervention, Project, Action, Contact, Select2MultipleField
from wtforms.fields import DateField, TelField
from flask_ckeditor import CKEditorField

def get_complet_name_label(user):
    return f"{user.firstname} {user.lastname}"

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

class LoginForm(FlaskForm):
    """
    Form for users to login
    """
    email = StringField(validators=[DataRequired(message=('Email is required!')), Email(message=('Email address Invalid!'))], render_kw={"placeholder":"EMail"})     
    password = PasswordField(validators=[DataRequired(message=('Password is required!'))], render_kw={"placeholder": ("Password"), "class":"form-control"})
    submit = SubmitField('LOGIN', render_kw={"class":"btn btn-lg btn-primary btn-block"})

class ResetPasswordForm(FlaskForm):
    """
    Form for Reseting Password
    """
    new_password = PasswordField(('NEW PASSWOR : '), validators=[
                                        DataRequired(), is_password_complex ,
                                        EqualTo('new_password2', message=('Passwords must match!')),
                                        Length(min=6, max=18, message=("Passwords must be 6 to 10 characters long!")),
                                        ], render_kw={"placeholder": ("Password"), "class":"form-control"})

    new_password2 = PasswordField('CONFIRM NEW PASSWORD : ',  render_kw={"placeholder": ("Confirm new Password"), "class":"form-control"})
    submit = SubmitField(('SAVE NEW PASSWORD'))

class EditEndUserForm(FlaskForm):
    """
    EDIT COUNT BY SIMPLE USER
    """
    firstname = StringField('FIRSTNAME :', validators=[DataRequired()])
    lastname = StringField('LASTNAME :', validators=[DataRequired()])
    function = StringField('FONCTION :', validators=[DataRequired()])
    phone = StringField('PHONE :', validators=[DataRequired()],render_kw={"disabled": "true"})
    email = StringField('E-MAIL :', validators=[DataRequired(), Email()],render_kw={"disabled": "true"})
    submit = SubmitField('SAVE')

class SupplierForm(FlaskForm):
    """
    SUPPLIER FORM
    """
    company_name = StringField('COMAPNY NAME :', validators=[DataRequired()])
    address = StringField('COMPANY ADDRESS :',validators=[DataRequired()])
    city = StringField('CITY :', validators=[DataRequired()])
    phone = StringField('PHONE :', validators=[DataRequired()])
    notes = CKEditorField('NOTES :', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 7})
    submit = SubmitField('SAVE')

class ContactForm(FlaskForm):
    """
    CONTACT FORMULAIRE
    """
    firstname = StringField('FIRSTNAME :', validators=[DataRequired()])
    lastname = StringField('LASTNAME :', validators=[DataRequired()])
    supplier = QuerySelectField('COMPANY NAME :', allow_blank=True, query_factory=lambda: Supplier.query.all(), get_label="company_name")
    email = StringField(' E-MAIL :', validators=[DataRequired(), Email()])
    phone = StringField('CONTACT PHONE :', validators=[DataRequired()])
    notes = TextAreaField('NOTES :', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 7})
    submit = SubmitField('SAVE')

class TicketForm(FlaskForm):
    """
    TICKETS FORMULAIRE
    """
    origin_ticket_number = HiddenField()
    ticket_number = StringField('TICKET NUMBER :', validators=[DataRequired()])
    open_date = DateField("""OPEN DATE :""", default=datetime.today, validators=[DataRequired()], render_kw={"placeholder": "Ex : 01-12-2020"})
    description = CKEditorField("""DESCRIPTION :""", validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 5})
    supplier = QuerySelectField('SUPPLIER :',query_factory=lambda: Supplier.query.all(), get_label="company_name")
    platform = QuerySelectField('DEVICE :',query_factory=lambda: Platform.query.all(), get_label="platform_name")
    admin = HiddenField('PERSON IN CHARGE :')

    priority = SelectField('PRIORITE :', choices =[
        ('HIGH','HIGH'),
        ('AVERAGE','AVERAGE'),
        ('LOW','LOW')])

    impact = SelectField('IMPACT :', choices =[
        ('HIGH','HIGH'),
        ('AVERAGE','AVERAGE'),
        ('LOW','LOW')])

    status = SelectField('STATUT:', choices =[
        ('OPEN','OPEN'),
        ('RESOLVED','RESOLVED'),
        ('CANCELED ','CANCELED')])

    resolution_date = HiddenField("""RESOLUTION DATE:""",render_kw={"placeholder": "01-12-2020"})
    comments = CKEditorField("""OBSERVATION :""", render_kw={'class': 'form-control', 'rows': 5} )
    submit = SubmitField('SAVE')

    
    def validate_ticket_number(self, field):
        TckNumber = Ticket.query.filter_by(ticket_number=field.data).first()
        if TckNumber and self.ticket_number.data != self.origin_ticket_number.data:
            raise ValidationError('Ticket Number is already in use!')

class InterventionForm(FlaskForm):
    """
    INTERVENTION FORMULAIRE
    """
    intervention_date = DateField('INTERVENTION DATE :',default=datetime.today, validators=[DataRequired()], render_kw={"placeholder": "Ex : 01-12-2020"}) 
    comment = CKEditorField('DESCRIPTION :', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 7})
    admin = QuerySelectField('INTERNAL COLLABORATOR :',allow_blank=True, query_factory=lambda: Admin.query.all(), get_label= get_complet_name_label)
    contact = QuerySelectField('EXTERNAL COLLABORATOR :',allow_blank=True, query_factory=lambda: Contact.query.all(), get_label=get_complet_name_label)
    submit = SubmitField('SAVE')

class Add_Note_vunerability(FlaskForm):
    vulnerabitlity_note = CKEditorField("", validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 5})
    submit = SubmitField('SAVE')

class ActionForm(FlaskForm):
    """
    ACTION FORMULAIRE
    """
    execution_date = DateField('EXECUTION DATE :', default=datetime.today, validators=[DataRequired()], render_kw={"placeholder": "Ex : 01-12-2020"})
    finish_date = DateField('FINISH DATE :', default=datetime.today, validators=[DataRequired()], render_kw={"placeholder": "Ex : 09-12-2020"})
    description = TextAreaField('DESCRIPTION :', validators=[DataRequired()], render_kw={'class': 'form-control', 'rows': 10})
    status = SelectField('STATUT:', choices =[
        ('PLANNED','PLANNED'),
        ('PROGRESS','IN PROGRESS'),
        ('COMPLETE','COMPLETE'),
        ('CANCELED ','CANCELED')])
    submit = SubmitField('SAVE')

class TagForm(FlaskForm):
    """
    TAG FORMULAIRE
    """
    tag_name = StringField('TAG NAME :',validators=[DataRequired()])
    tag_description = StringField('TAG DESCRIPTION :', validators=[DataRequired()], render_kw={"placeholder": "Describe your TAG"})
    tag_color = StringField('TAG COLOR :', validators=[DataRequired()], render_kw={"type": "color"})
    submit = SubmitField('SAVE')