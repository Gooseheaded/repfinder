#
# This defines the web server's API endpoints.
#

from flask import Flask, make_response, render_template, request
from repfinder import Repfinder
import rfsettings
import rfdb
import webbrowser
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
    return render_template('index.html', settings=settings)

@app.get("/replays")
def listReplays():
    results = db.replays.copy()
    # TODO: Receive a single "query" param, and parse it into alias/map/race.

    aliasesFilter = request.args.get('aliases', default='').split(' ')
    if len(aliasesFilter) > 0:
        results = repfinder.filterReplaysByAliases(results, aliasesFilter)

    mapFilter = request.args.get('map', default='')
    if mapFilter != '':
        results = repfinder.filterReplaysByMapName(results, mapFilter)
    
    raceFilter = request.args.get('race', default='')
    if raceFilter != '':
        results = repfinder.filterReplaysByRace(results, raceFilter)
    
    print(len(aliasesFilter))
    if request.args.get('aliases', default='') == '' and mapFilter == '' and raceFilter == '':
        results = {}
    return render_template('replays_list.html', replays=enumerate(results.values()))
    

@app.post("/scan")
def scanReplays():
    repfinder.syncDb()
    return render_template('scan_progress.html', progressPercentage=0)
    # global settings
    # repfinder.syncDb()

@app.get("/scan")
def scanStart():
    return render_template('scan_start.html', progressPercentage=0)

# TODO: later
progressTest = 0
@app.get("/scan/progress")
def scanProgress():
    global progressTest
    progressTest += 100

    print(f"Progress is at {progressTest}%...")
    if progressTest == 100:
        resp = make_response(render_template('scan_progress.html', progressPercentage=0))
        resp.headers['HX-Trigger'] = 'done'
        progressTest = 0
        return resp
    
    return render_template('scan_progress.html', progressPercentage=progressTest)