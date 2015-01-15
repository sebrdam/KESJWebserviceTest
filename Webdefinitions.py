from flask import Flask, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth
from peewee import *

db = MySQLDatabase('kesjwebservice', user='kesj',passwd='kesj123')

class Webdefinitions(Model):
    provider = CharField()
    category = CharField()
    subcategory = CharField()
    url = CharField()
    pattern = CharField()
    subpattern_price = CharField()
    subpattern_link = CharField()
    subpattern_description = CharField()
    picurl = CharField()
    subpattern_data = CharField()
    
    class Meta:
        database = db

def get_webdefinitions():
	returnArray = []
	for webdef in Webdefinitions.select():
		singleWebdef = {
			'provider': webdef.provider,
			'category': webdef.category,
			'subcategory': webdef.subcategory,
			'url': webdef.url,
			'pattern': webdef.pattern,
			'subpatternprijs': webdef.subpattern_price,
			'subpatternlink': webdef.subpattern_link,
			'subpatternomschrijving': webdef.subpattern_description,
			'picurl': webdef.picurl,
			'subpatterndata': webdef.subpattern_data
		}
		returnArray.append(singleWebdef)
	return jsonify(data = returnArray)

