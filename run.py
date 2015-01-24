from flask import Flask, jsonify, request, make_response, render_template
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.basicauth import BasicAuth
from Webdefinitions import *
from Rawdata import *
from neo4jrestclient.client import GraphDatabase
import json
from datetime import timedelta
from functools import update_wrapper

app = Flask(__name__)

gdb = GraphDatabase("http://localhost:7474/db/data/")

webdefinitions = Webdefinitions()

basic_auth = BasicAuth(app)

app.config['BASIC_AUTH_USERNAME'] = 'user'
app.config['BASIC_AUTH_PASSWORD'] = '1234'


users = {
    'kesj': 'kesj',
    'edwin': 'edwin',
    'sebastiaan': 'sebastiaan',
    'user': '1234'
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

##@auth.login_required
@app.route('/crawler/post', methods=['POST'])
@basic_auth.required
def crawler_post(): 
    ## get the Json data
    content = request.get_json()
    ## Read the Json data
    for item in content['data']:
        ## get the specific fields from Json
        url = item['linkurl']
        omschrijving = item["omschrijving"]
        prijs = item["prijs"]
        category = item["category"]
        dataspecs = item["dataspecs"]
        provider = item["provider"]
    return 'Loggedin post accepted'

@app.route('/crawler/process')
def crawler_process():
	return process_data()
	
@app.route('/crawler/process_price')
def crawler_process_price():
	return process_price_data()

@app.route("/results/<input>/<input1>", methods=['GET'])
@crossdomain(origin='*')
def get_results(input, input1):
    results = input
    results1 = input1
    ##null
    if results1 == 'null':
        query = 'MATCH (n:`' + results + '`) RETURN n'
        results = gdb.query(query, data_contents=True)
        return json.dumps(results.rows)
    ##return input
    else:
        reinput1 = re.sub("[^a-zA-Z0-9]", "",results1)
        query = 'START n=node(*) MATCH (n:`' + results + '`)-[:`' + reinput1 + '`]->(m) RETURN n'
        results = gdb.query(query, data_contents=True)
        return json.dumps(results.rows) 


@app.route("/prijsvergelijk/<input>", methods=['GET'])
@crossdomain(origin='*')
def get_resultsprijs(input):
    results = input
    queryprijs = 'START n=node(*) MATCH (n {id:' + results + '})-[:`PrijsVergelijk`]-(m) RETURN n,m'
    
    resultsprijs = gdb.query(queryprijs, data_contents=True)
    return json.dumps(resultsprijs.rows)
    
    
    
    
if __name__ == '__main__':
	app.run(host='0.0.0.0', port = 80, debug=True)
