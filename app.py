#
# This defines the web server's API endpoints.
#

from flask import Flask, render_template
import rfsettings

app = Flask(__name__)
settings = rfsettings.init()

@app.route("/")
def index():
    global settings
    
    settings = rfsettings.init()
    return render_template('index.html', settings=settings)