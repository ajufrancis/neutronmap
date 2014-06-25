# -*- coding: utf-8 -*-

from flask import Flask, json, render_template, request, Response

from forms import AuthenticationForm
from core import LogicalTopology

app = Flask(__name__)
app.config.from_object('config')


@app.route('/', methods=['GET'])
def index():
    """Application entry point."""
    return render_template('index.html')


@app.route('/topology', methods=['POST'])
def topology():
    """Returns a JSON representation of a Neutron topology."""
    form = AuthenticationForm(request.form)

    if request.method == 'POST' and form.validate():
        # We need positional arguments for nova client
        # and keywords arguments for neutron client
        keys = ['username', 'password', 'tenant_name', 'auth_url']
        args = [getattr(form, key).data for key in keys]
        kwargs = dict(zip(keys, args))

        try:
            topology = LogicalTopology(*args, **kwargs)
            return Response(response=topology.dumps(),
                            mimetype='application/json',
                            status=200)
        except Exception as e:
            try:
                # Handling of Neutron client exceptions first
                error = json.loads(e.message).pop('error')
                status = error.get('code', 500)
            except ValueError:
                # Wrap Nova client and other exceptions
                # into a serializable object
                status = e.http_status if hasattr(e, 'http_status') else 500
                error = {'title': type(e).__name__,
                         'message': str(e),
                         'code': status}
            return Response(response=json.dumps(error),
                            mimetype='application/json',
                            status=status)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
