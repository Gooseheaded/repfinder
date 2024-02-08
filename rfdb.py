from typing import List
from pathlib import Path
from enum import Enum
import json


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
        return f'{"text": "{self.text}", "labelColor": "{self.labelColor.name}""}'


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
    def __init__(self, path: Path, mapName: str, aliases: List[AliasAndRace], labels: List[Label]=None):
        self.path = path.resolve()
        self.mapName = mapName
        self.aliases = aliases.copy()
        if labels is None: 
            self.labels = []
        else:
            self.labels = labels.copy()

    def toJSON(self) -> str:
        jsonAliases = [alias.toJSON() for alias in self.aliases]
        return f'{{"path": "{str(self.path.as_posix())}", "mapName": "{self.mapName}", "aliases": [{", ".join(jsonAliases)}]}}'


class RFDB():
    def __init__(self, dbPath: Path):
        self._dbPath = dbPath
        self._replays = dict()
        self._labelDefs = set()
        self._playerDefs = dict()

    def load(self):
        # TODO: Open the json dbs and parse them.
        pass

    def save(self):
        # TODO: Abstract away storage
        # TODO: Sweet mother mercy please do this whole serialization the right way
        replaysJsonStrs = []
        for replay in self._replays.values():
            replaysJsonStrs.append(replay.toJSON())

        playerDefsJsonStrs = []
        for playerDef in self._playerDefs:
            playerDefsJsonStrs.append(playerDef.toJSON())

        labelDefsJsonStrs = []
        for labelDef in self._labelDefs:
            labelDefsJsonStrs.append(labelDef.toJSON())
        saveJsonStr = "{"
        saveJsonStr += "\"replays\": ["
        saveJsonStr +=  ",".join(replaysJsonStrs)
        saveJsonStr += "],"
        saveJsonStr += "\"playerDefs\": ["
        saveJsonStr +=  ",".join(playerDefsJsonStrs)
        saveJsonStr += "],"
        saveJsonStr += "\"labelDefs\": ["
        saveJsonStr +=  ",".join(labelDefsJsonStrs)
        saveJsonStr += "]"
        saveJsonStr += "}"

        with open(Path(self._dbPath) / "rfdb.json", "w") as dbFile:
            dbFile.write(saveJsonStr)
        return True

    def createReplay(self, replay: Replay):
        self._replays[str(replay.path)] = replay
        return self.save()
    
    def readReplay(self, path: Path):
        path = path.resolve()
        if not path.is_file():
            raise Exception(f"There is no replay at the given path: {path}")
        if not path in self._replays:
            # TODO: Avoid using None.
            return None        
        return self._replays[path]

    def deleteReplay(self, replay: Replay):
        del self._replays[str(replay.path)]
        self.save()

    def createPlayer(self, player: Player):
        self._playerDefs[player.primaryAlias] = player
        self.save()

    def deletePlayer(self, player: Player):
        del self._playerDefs[player.primaryAlias]
        self.save()

    def createLabel(self, label: Label):
        self._labelDefs.add(label)
        self.save()

    def deleteLabel(self, label: Label):
        self._labelDefs.discard(label)
        # TODO: Remove all references to this label from replays.
        self.save()

    def toJSON():
        # TODO: This whole thing.
        return json.dumps()
