# -*- coding: utf-8 -*-

from flask import Flask, json, render_template, request

from forms import AuthenticationForm
from core import LogicalTopology


app = Flask(__name__)
app.config.from_object('config')


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


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
