from typing import List
from pathlib import Path
import hashlib
from enum import Enum
import json
from human_id import generate_id


class LabelColor(Enum):
    Blue = "primary"
    Gray = "secondary"
    Green = "success"
    Red = "danger"
    Yellow = "warning"
    Cyan = "info"
    Light = "light"
    Dark = "dark"


class Label():
    def __init__(self, text: str, labelColor: LabelColor):
        self.text = text
        self.labelColor = labelColor

    # NOTE: Not actually needed. This should happen in a Jinja template.
    def toHTML(self):
        return f'<span class="badge rounded-pill text-bg-{self.labelColor.value}">{self.text}</span>'

    def toJSON(self):
        return f'{{"text": "{self.text}", "labelColor": "{self.labelColor.name}"}}'


class Race(Enum):
    Protoss = "Protoss"
    Terran = "Terran"
    Zerg = "Zerg"


class Player():
    def __init__(self, primaryAlias: str, aliases: List[str]):
        self.primaryAlias = primaryAlias
        self.aliases = set(aliases.copy())
        self.aliases.add(self.primaryAlias)

    def toJSON(self) -> str:
        quotedAliases = [f'"{alias}"' for alias in self.aliases]
        return f'{{"primaryAlias": "{self.primaryAlias}", "aliases": [{", ".join(quotedAliases)}]}}'


class AliasAndRace():
    def __init__(self, alias: str, race: Race):
        self.alias = alias
        self.race = race

    def toJSON(self) -> str:
        return f'{{"alias": "{self.alias}", "race": "{self.race}"}}'


class Replay():
    def __init__(self, path: Path, mapName: str, aliases: List[AliasAndRace], labels: List[Label] = None):
        self.path = path.resolve()
        self.id = generate_id(seed=self.path.name, word_count=5)
        self.mapName = mapName
        self.aliases = aliases.copy()
        if labels is None:
            self.labels = []
        else:
            self.labels = labels.copy()

    def toJSON(self) -> str:
        jsonAliases = [alias.toJSON() for alias in self.aliases]
        jsonLabels = [label.toJSON() for label in self.labels]
        return f'{{"path": "{str(self.path.as_posix())}", "mapName": "{self.mapName}", "aliases": [{", ".join(jsonAliases)}], "labels": [{", ".join(jsonAliases)}]}}'


class RFDB():
    def __init__(self, dbPath: Path):
        self._dbPath = dbPath
        self.replays = dict()
        self.labelDefs = set()
        self.playerDefs = dict()

        if not Path(dbPath / "rfdb.json").is_file():
            with open(dbPath, "w") as dbf:
                dbf.write(r"""{"replays":[], "labelDefs":[], "playerDefs":[]}""")

    def load(self):
        with open(Path(self._dbPath, "rfdb.json"), "r") as dbFile:
            dbJson = json.loads(dbFile.read())

            replaysJson = dbJson["replays"]
            for replayJson in replaysJson:
                parsedAliases = [AliasAndRace(
                    entry["alias"], entry["race"]) for entry in replayJson["aliases"]]
                replay = Replay(path=Path(replayJson["path"]).resolve(),
                                mapName=replayJson["mapName"],
                                aliases=parsedAliases,
                                labels=replayJson["labels"])
                self.replays[replay.id] = replay
        # TODO: Parse label definitions and player definitions.
            # self._labelDefs = parse dbJson["labelDefs"]
            # self._playerDefs = parse dbJson["playerDefs"]
            return True

    def save(self):
        # TODO: Abstract away storage
        # TODO: Sweet mother mercy please do this whole serialization the right way
        replaysJsonStrs = []
        for replay in self.replays.values():
            replaysJsonStrs.append(replay.toJSON())

        playerDefsJsonStrs = []
        for playerDef in self.playerDefs:
            playerDefsJsonStrs.append(playerDef.toJSON())

        labelDefsJsonStrs = []
        for labelDef in self.labelDefs:
            labelDefsJsonStrs.append(labelDef.toJSON())
        saveJsonStr = "{"
        saveJsonStr += "\"replays\": ["
        saveJsonStr += ",".join(replaysJsonStrs)
        saveJsonStr += "],"
        saveJsonStr += "\"playerDefs\": ["
        saveJsonStr += ",".join(playerDefsJsonStrs)
        saveJsonStr += "],"
        saveJsonStr += "\"labelDefs\": ["
        saveJsonStr += ",".join(labelDefsJsonStrs)
        saveJsonStr += "]"
        saveJsonStr += "}"

        with open(Path(self._dbPath) / "rfdb.json", "w") as dbFile:
            dbFile.write(saveJsonStr)
        return True

    def createReplay(self, replay: Replay):
        self.replays[replay.id] = replay
        return self.save()

    def readReplay(self, id: str):
        if id in self.replays:
            return self.replays[id]
        return None

    def deleteReplay(self, replay: Replay):
        del self.replays[replay.id]
        self.save()

    def createPlayer(self, player: Player):
        self.playerDefs[player.primaryAlias] = player
        self.save()

    def deletePlayer(self, player: Player):
        del self.playerDefs[player.primaryAlias]
        self.save()

    def createLabel(self, label: Label):
        self.labelDefs.add(label)
        self.save()

    def deleteLabel(self, label: Label):
        self.labelDefs.discard(label)
        # TODO: Remove all references to this label from replays.
        self.save()

    def toJSON():
        # TODO: This whole thing.
        return json.dumps()
