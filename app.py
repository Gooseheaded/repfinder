#
# This defines the web server's API endpoints.
#

from flask import Flask, render_template
from repfinder import Repfinder
import rfsettings
import rfdb
import webbrowser
from pathlib import Path

app = Flask(__name__)
settings = rfsettings.init()
webbrowser.open_new_tab("http://localhost:5000")

@app.route("/")
def index():
    global settings

    # Testing serialization.
    print(f"settings.dbPath is {settings.dbPath} ({type(settings.dbPath)})")
    testDb = rfdb.RFDB(settings.dbPath)
    repfinder = Repfinder(settings, testDb)
    # repfinder.registerReplay(Path("C:/Users/gctrindade local/Documents/Starcraft/maps/replays/coach fuzzy fac block.rep").resolve())
    repfinder.syncDb()
    return render_template('index.html', settings=settings)

def test():
    global settings
