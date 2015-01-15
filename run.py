from flask import Flask, jsonify, request, make_response, render_template
from flask.ext.httpauth import HTTPBasicAuth
from Webdefinitions import *
from Rawdata import *
from neo4jrestclient.client import GraphDatabase
import json
from datetime import timedelta
from functools import update_wrapper

app = Flask(__name__)
auth = HTTPBasicAuth()

gdb = GraphDatabase("http://localhost:7474/db/data/")

webdefinitions = Webdefinitions()


users = {
    'kesj': '***',
    'edwin': '****',
    'sebastiaan': '****',
    'user': '****'
}

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/crawler/get', methods=['GET'])
def crawler_get():
	return get_webdefinitions()

@app.route('/crawler/post', methods=['POST'])
@auth.login_required
def crawler_post():
	data = {
		'category': request.form['category'],
		'subcategory': request.form['subcategory'],
		'linkurl': request.form['linkurl'],
		'omschrijving': request.form['omschrijving'],
		'prijs': request.form['prijs'],
		'provider': request.form['provider'],
		'dataspecs': request.form['dataspecs'],
		'picurl': request.form['picurl']
	}
	return post_data(data)

@app.route('/crawler/process')
def crawler_process():
	return process_data()

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route("/results/<input>", methods=['GET'])
@crossdomain(origin='*')
def get_results(input):
    results = input
    query = 'MATCH (n:`' + results + '`) RETURN n'
    results = gdb.query(query, data_contents=True)
    return json.dumps(results.rows)
    
if __name__ == '__main__':
	app.run(host='0.0.0.0', port = 80, debug=True)
