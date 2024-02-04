from typing import List
from pathlib import Path
from enum import Enum, auto
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
        return json.dumps({"text": self.text, "labelColor": self.labelColor.name})


class Race(Enum):
    Protoss = auto()
    Terran = auto()
    Zerg = auto()


class Player():
    def __init__(self, primaryAlias: str, aliases: List[str]):
        self.primaryAlias = primaryAlias
        self.aliases = set(aliases.copy())
        self.aliases.add(self.primaryAlias)

    def toJSON(self) -> str:
        return json.dumps({"primaryAlias": self.primaryAlias, "aliases": list(self.aliases)})


class AliasAndRace():
    def __init__(self, player: Player, race: Race):
        self.alias = player.primaryAlias
        self.race = race.name

    def toJSON(self) -> str:
        return json.dumps({"alias": self.alias, "race": self.race})


class Map():
    def __init__(self, name: str, playerCount: int, previewImagePath: Path):
        self.name = name
        self.playerCount = playerCount
        self.previewImagePath = previewImagePath.resolve()

    def toJSON(self) -> str:
        return json.dumps({"name": self.name, "playerCount": self.playerCount, "previewImagePath": str(self.previewImagePath)})


class Replay():
    def __init__(self, path: Path, map: Map, players: List[AliasAndRace], labels: List[Label]):
        self.path = path.resolve()
        self.mapName = map.name
        self.players = players.copy()
        self.labels = labels.copy()

    def toJSON(self) -> str:
        # TODO: Properly serialize self.players array instead of JSON-stringifying it.
        # TODO: serialize labels
        return json.dumps({"path": str(self.path), "mapName": self.mapName, "players": [player.toJSON() for player in self.players]})


class RFDB():
    def __init__(self, dbPath: Path):
        self._dbPath = dbPath.resolve()
        self._replays = set()
        self._labelDefs = set()
        self._playerDefs = dict()

    def load(self):
        # TODO: Open the json dbs and parse them.
        pass

    def save(self):
        # TODO: Serialize replays, and write to the replay json db.
        # TODO: Serialize label definitions, and write to the labels json db.
        # TODO: Serialize player definitions, and write to the players json db.
        pass

    def addReplay(self, replay: Replay):
        self._replays.add(replay)
        self.save()

    def removeReplay(self, replay: Replay):
        self._replays.discard(replay)
        self.save()

    def addPlayer(self, player: Player):
        self._playerDefs[player.primaryAlias] = player
        self.save()

    def removePlayer(self, player: Player):
        del self._playerDefs[player.primaryAlias]
        self.save()

    def addLabel(self, label: Label):
        self._labelDefs.add(label)
        self.save()

    def removeLabel(self, label: Label):
        self._labelDefs.discard(label)
        # TODO: Remove all references to this label from replays.
        self.save()

    def toJSON():
        # TODO: This whole thing.
        return json.dumps()
