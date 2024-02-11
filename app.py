#
# This defines the web server"s API endpoints.
#

from flask import Flask, make_response, render_template, request
from repfinder import Repfinder
import rfsettings
import rfdb
import webbrowser
import sys
import subprocess
from pathlib import Path

app = Flask(__name__)
settings = rfsettings.init()
db = rfdb.RFDB(settings.dbDirPath)
db.load()
repfinder = Repfinder(settings, db)
webbrowser.open_new_tab("http://localhost:5000")

# This needs to happen O N C E
# repfinder.syncDb()


@app.route("/")
def index():    
    return render_template("index.jinja2", settings=settings)

@app.get("/replays")
def listReplays():
    results = db.replays.copy()
    # TODO: Receive a single "query" param, and parse it into alias/map/race.

    aliasesFilter = request.args.get("aliases", default="").split(" ")
    if len(aliasesFilter) > 0:
        results = repfinder.filterReplaysByAliases(results, aliasesFilter)

    mapFilter = request.args.get("map", default="")
    if mapFilter != "":
        results = repfinder.filterReplaysByMapName(results, mapFilter)
    
    raceFilter = request.args.get("race", default="")
    if raceFilter != "":
        results = repfinder.filterReplaysByRace(results, raceFilter)
    
    print(len(aliasesFilter))
    if request.args.get("aliases", default="") == "" and mapFilter == "" and raceFilter == "":
        results = {}
    return render_template("replays_list.jinja2", replays=enumerate(results.values()))

@app.get("/replay/<string:replayId>")
def openReplay(replayId):
    replay = repfinder.getReplayById(replayId)
    if replay is None:
         return "Open"
    if sys.platform == "darwin":
        subprocess.check_call(["open", "--", replay.path.parent])
    elif sys.platform == "linux2":
        subprocess.check_call(["xdg-open", "--", replay.path.parent])
    elif sys.platform == "win32":
        # Explorer.exe always returns 1, so `call_check` will report a non-zero exit status as failure.
        subprocess.call(["explorer", replay.path])
    return "Open"
    

@app.post("/scan")
def scanReplays():
    repfinder.syncDb()
    return render_template("scan_progress.jinja2", progressPercentage=0)
    # global settings
    # repfinder.syncDb()

@app.get("/scan")
def scanStart():
    return render_template("scan_start.jinja2", progressPercentage=0)

# TODO: later
progressTest = 0
@app.get("/scan/progress")
def scanProgress():
    global progressTest
    progressTest += 100

    print(f"Progress is at {progressTest}%...")
    if progressTest == 100:
        resp = make_response(render_template("scan_progress.jinja2", progressPercentage=0))
        resp.headers["HX-Trigger"] = "done"
        progressTest = 0
        return resp
    
    return render_template("scan_progress.jinja2", progressPercentage=progressTest)