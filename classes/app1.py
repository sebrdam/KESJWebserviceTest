#!/Python34/python

from flask import Flask, render_template

app = Flask('app1')
# webcode = open('welcome.html').read() - not needed

@app.route('/')
def webprint():
    return render_template('welcom.html') 

if __name__ == '__main__':
    app.run(port = 3000)