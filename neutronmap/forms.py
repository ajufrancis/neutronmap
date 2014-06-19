# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import PasswordField
from wtforms import StringField

from wtforms.validators import required


class AuthenticationForm(Form):
    """Form for specifying Keystone credentials
       along with the target tenant.

    """

    username = StringField('username', [required()])
    password = PasswordField('password', [required()])
    tenant_name = StringField('tenant_name', [required()])
    auth_url = StringField('auth_url', [required()])
