# -*- coding: utf-8 -*-

from wtforms import Form, PasswordField, StringField
from wtforms.validators import required


class AuthenticationForm(Form):
    """Form for Keystone authentication."""

    username = StringField('username', [required()])
    password = PasswordField('password', [required()])
    tenant_name = StringField('tenant_name', [required()])
    auth_url = StringField('auth_url', [required()])
