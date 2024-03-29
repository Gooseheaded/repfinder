#
# This defines the web server"s API endpoints.
#
import math
from pathlib import Path
import threading
import time
import pyperclip
from PyQt5.QtCore import Qt, QUrl, QRect, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

from flask import Flask, make_response, render_template, request, url_for
from repfinder import Repfinder
import rfsettings
import rfdb
import webbrowser
import sys

flaskApp = Flask(__name__)
qtApp = None
settings = rfsettings.init()
db = rfdb.RFDB(settings.dbDirPath)
db.load()
repfinder = Repfinder(settings, db)


@flaskApp.put("/clipboard")
def clipboard():
    replayPath = request.form.get("replayPath", default="")
    if (replayPath := Path(replayPath)).is_file():
        pyperclip.copy(str(replayPath))
        return "OK"
    else:
        # TODO: Log this. Suspicious error.
        return "ERROR"

@flaskApp.route("/")
def index():    
    return render_template("index.jinja2",
                           settings=settings,
                           urlForIndexing=url_for("indexReplays"))

@flaskApp.get("/replays")
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
    return render_template("components/replays.jinja2", replays=enumerate(results.values()), replayCount=len(results.values()))

@flaskApp.get("/replays/<string:replayId>")
def openReplay(replayId):
    replay = repfinder.getReplayById(replayId)
    if replay is None:
         return "Open"
    webbrowser.open(replay.path)
    return "Open"

@flaskApp.post("/index")
def indexReplays():
    # TODO: async this
    if repfinder.indexReplays():
        return render_template("indexing/indexing-progress.jinja2",
                               progressPercentage=0)
    else:
        return render_template("indexing/indexing-start.jinja2",
                               urlForIndexing=url_for("indexReplays"))

@flaskApp.get("/index")
def getIndexingProgress():
    progress = repfinder.replayIndexer.getProgress()
    if progress < 1:
        return render_template("indexing/indexing-progress.jinja2",
                        urlForProgress="/index",
                        progressPercentage=math.floor(progress * 100) / 100,
                        replaysToDoCount=repfinder.replayIndexer.replaysToDoCount,
                        replaysDoneCount=repfinder.replayIndexer.replaysDoneCount)
    else:
        return render_template("indexing/indexing-summary.jinja2",
                        replaysDoneCount=repfinder.replayIndexer.replaysDoneCount)

@flaskApp.get("/labels")
def listLabels():
    # TODO: implement
    pass

@flaskApp.post("/labels")
def createLabel():
    # TODO: implement
    labelText = request.args.get("text", default="")
    labelColor = request.form.get("color", default="")
    pass

@flaskApp.delete("/labels/<string:labelText>")
def deleteLabel(labelText):
    # TODO: implement
    pass

@flaskApp.post("/replays/<string:replayId>/label/<string:labelText>")
def addLabelToReplay(replayId:str, labelText:str):
    # TODO: implement
    pass

@flaskApp.delete("/replays/<string:replayId>/label/<string:labelText>")
def removeLabelFromReplay(replayId:str, labelText:str):
    # TODO: implement
    pass

@flaskApp.get("/players")
def listPlayers():
    # TODO: implement
    pass

@flaskApp.post("/players")
def createPlayer():
    # TODO: implement
    primaryAlias = request.form.get("primaryAlias", default="")
    pass

@flaskApp.get("/players/<string:primaryAlias>")
def getPlayer(primaryAlias:str):
    # TODO: implement
    pass

@flaskApp.delete("/players/<string:primaryAlias>")
def deletePlayer(primaryAlias:str):
    # TODO: implement
    pass

@flaskApp.post("/players/<string:primaryAlias>")
def addAliasToPlayer(primaryAlias:str):
    # TODO: implement
    newAlias = request.form.get("alias", default="")
    pass

#
# This creates the little window.
#

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.webView = QWebEngineView()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.webView)
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("Repfinder v24.03.21")
        
        _w = 1600
        _h = 900
        screenSize = qtApp.primaryScreen().size()
        topLeft = QPoint(screenSize.width() // 2 - _w // 2, screenSize.height() // 2 - _h // 2)
        bottomRight = QPoint(screenSize.width() // 2 + _w // 2, screenSize.height() // 2 + _h // 2)
        self.setGeometry(QRect(topLeft, bottomRight))

        self.flaskThread = threading.Thread(target=flaskApp.run)
        self.flaskThread.daemon = True # The thread dies when the parent process dies.
        self.flaskThread.start()

        self.webView.load(QUrl("http://localhost:5000/"))
    
    def closeEvent(self, event):
        super().closeEvent(event)  # Call base class implementation first        
        QApplication.instance().quit()


if __name__ == "__main__":
    # Create and start the Qt application
    qtApp = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

     # Run the Qt event loop
    sys.exit(qtApp.exec_())