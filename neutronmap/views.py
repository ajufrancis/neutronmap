# -*- coding: utf-8 -*-

from core import LogicalTopology
from flask import json, render_template, request
from forms import AuthenticationForm
from neutronmap import app


@app.route('/', methods=['GET', 'POST'])
def index():
    """Application entry point."""

    error = None
    status = None
    form = AuthenticationForm(request.form)

    if request.method == 'POST' and form.validate():
        # We need positional arguments for nova client
        # and keywords arguments for neutron client
        keys = ['username', 'password', 'tenant_name', 'auth_url']
        args = [getattr(form, key).data for key in keys]
        kwargs = dict(zip(keys, args))

        try:
            topology = LogicalTopology(*args, **kwargs)
            return render_template('map.html', data=topology.dumps(),
                                   tenant_name=kwargs['tenant_name'],
                                   auth_url=kwargs['auth_url']), 200
        except Exception as e:
            try:
                # Handle Neutron client exceptions first
                error = json.loads(e.message).pop('error')
                status = error.get('code', 500)
            except ValueError:
                # Wrap Nova client and other exceptions
                # into a serializable object
                status = getattr(e, 'http_status', 500)
                error = {'title': type(e).__name__,
                         'message': str(e),
                         'code': status}

    return render_template('index.html', form=form, error=error), status


@app.errorhandler(500)
def internal_server_error(error):
    """In case the worst happens."""

    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found(error):
    """Another classic."""

    return render_template('errors/404.html'), 404
