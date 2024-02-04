import configparser
from pathlib import Path
from enum import Enum, auto

class SettingsStatus(Enum):
    UNINITIALIZED = auto()
    SCREP_MISSING = auto()
    REPLAYS_MISSING = auto()
    OK = auto()

class Settings():
    def __init__(self, filePath: Path, screpPath: Path, replaysPath: Path, status: SettingsStatus):
        self.filePath = filePath
        self.screpPath = screpPath
        self.replaysPath = replaysPath
        self.status = status

def init() -> Settings:
    settingsPath = Path(Path.cwd(), "repfinder_settings.ini").resolve()
    parser = configparser.ConfigParser()

    if not settingsPath.is_file():
        parser['repfinder'] = {
            'screp_path': '<Your screp path goes here>',
            'replays_folder': '<Your replays folder goes here>',
        }
        with open(settingsPath, "w") as settingsFile:
            parser.write(settingsFile)
        print(f"Please edit your settings at '{settingsPath}'.")
        return Settings(filePath=settingsPath, screpPath=None, replaysPath=None, status=SettingsStatus.UNINITIALIZED)

    parser.read(settingsPath)

    screpPath = parser["repfinder"]["screp_path"].replace("\"", "").replace("\'", "")
    screpPathRes = Path(screpPath).resolve()
    if not screpPathRes.is_file():
        print(f"screp could not be found. Check if the path is correct in your settings file ('{settingsPath}'):\n'{screpPath}'")
        return Settings(filePath=settingsPath, screpPath=screpPath, replaysPath=None, status=SettingsStatus.SCREP_MISSING)

    replaysPath = parser["repfinder"]["replays_folder"].replace("\"", "").replace("\'", "")
    replaysPathRes = Path(replaysPath).resolve()
    if not replaysPathRes.is_dir():
        print(f"The replays folder could not be found. Check if the path is correct in your settings file ('{settingsPath}'):\n'{replaysPath}'")
        return Settings(filePath=settingsPath, screpPath=screpPathRes, replaysPath=replaysPath, status=SettingsStatus.REPLAYS_MISSING)

    return Settings(filePath=settingsPath, screpPath=screpPathRes, replaysPath=replaysPathRes, status=SettingsStatus.OK)