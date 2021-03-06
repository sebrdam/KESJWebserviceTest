from flask import Flask, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth
from peewee import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.client import Node
import time
import pprint
import re
import urllib

db = MySQLDatabase('kesjwebservice', user='kesj',passwd='kesj123')
gdb = GraphDatabase("http://localhost:7474/db/data/")

class Rawdata(Model):
    id = IntegerField()
    provider = CharField()
    category = CharField()
    subcategory = CharField()
    linkurl = CharField()
    omschrijving = CharField()
    prijs = CharField()
    picurl = CharField()
    timestamp = DateTimeField()

    class Meta:
        database = db

def post_data(data):
    q = Rawdata.insert(provider=data['provider'], category=data['category'], subcategory=data['subcategory'], linkurl=data['linkurl'], omschrijving=data['omschrijving'], prijs=data['prijs'], picurl=data['picurl'], timestamp=time.strftime("%Y-%m-%d %H:%M:%S"))
    q.execute()
    return jsonify(data = 'Succesful')

def process_data():
    for rawdata in Rawdata.select():
        label = gdb.labels.create(rawdata.category)
        label1 = gdb.labels.create(rawdata.subcategory)
        ## try to see if node already exists
        ##if the url attribute is the same than update node
        query2 = 'MATCH (n {url:"' + rawdata.linkurl + '"}) RETURN n'
        mynode = gdb.query(query2, returns=Node)
        if mynode:
            ## if exists update node with new price
            query3 = 'MATCH (n {url:"' + rawdata.linkurl + '"}) SET n.prijs_'+ rawdata.timestamp.strftime('%Y%m%d%H%M%S') +' = '+ rawdata.prijs +', n.prijs = '+rawdata.prijs+', n.omschrijving = "'+rawdata.omschrijving+'", n.picurl = "'+rawdata.picurl+'"'
            mynode1 = gdb.query(query3, returns=Node)

        ##else create the node
        else:
            comp = gdb.nodes.create(name=rawdata.category, omschrijving=rawdata.omschrijving, prijs=rawdata.prijs, maincategory=rawdata.category, subcategory=rawdata.subcategory, provider=rawdata.provider, url=rawdata.linkurl, picurl=rawdata.picurl, id=rawdata.id)
            label.add(comp)

            queryHoofdNode = 'MATCH (n {naam:"' + rawdata.subcategory + '"}) RETURN n'
            hoofdnode = gdb.query(queryHoofdNode, returns=Node)
            if hoofdnode:
                print 'Skipped---'
            else:
                newHoofdNodeLabel = gdb.labels.create(rawdata.subcategory)
                newHoofdNode = gdb.nodes.create(naam=rawdata.subcategory)
                newHoofdNodeLabel.add(newHoofdNode)
                hoofdnode = gdb.query(queryHoofdNode, returns=Node)
            relQuery = 'MATCH (comp {url:"' + rawdata.linkurl + '"}) MATCH (hoofdnode {naam:"' + rawdata.subcategory + '"}) CREATE (comp)-[:'+re.sub("[^a-zA-Z0-9]", "",rawdata.subcategory)+']->(hoofdnode)'
            relationship = gdb.query(relQuery)
    return 'Done'
    
def process_price_data():
	for rawdata in Rawdata.select().where(Rawdata.provider == 'http://www.informatique.nl'):
		alternateData = Rawdata.get(Rawdata.omschrijving.contains(rawdata.omschrijving))
		if alternateData.linkurl:
			relQuery = 'MATCH (infcomp {url:"' + rawdata.linkurl + '"}) MATCH (altcomp {url:"' + alternateData.linkurl + '"}) CREATE (infcomp)-[:PrijsVergelijk]->(altcomp)'
			relationship = gdb.query(relQuery)
	return 'Done'
