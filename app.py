#
# This defines the web server's API endpoints.
#

from flask import Flask, render_template
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
    testPlayer = rfdb.Player("Gooseheaded", ["NCs]Gus", "CPL-Goose"])
    print(f"testPlayer: {testPlayer.toJSON()}")

    testAliasAndRace = rfdb.AliasAndRace(testPlayer, rfdb.Race.Zerg)
    print(f"testAliasAndRace: {testAliasAndRace.toJSON()}")

    testMap = rfdb.Map("Destination", 2, Path.cwd())
    print(f"testMap: {testMap.toJSON()}")

    testReplay = rfdb.Replay(Path.cwd(), testMap, [testAliasAndRace])
    print(f"testReplay: {testReplay.toJSON()}")

    settings = rfsettings.init()
    return render_template('index.html', settings=settings)