import configparser
from pathlib import Path
from enum import Enum, auto

class SettingsStatus(Enum):
    UNINITIALIZED = auto()
    SCREP_MISSING = auto()
    REPLAYS_MISSING = auto()
    DB_MISSING = auto()
    OK = auto()

class Settings():
    def __init__(self, filePath: Path, screpPath: Path, replaysPath: Path, dbPath: Path, status: SettingsStatus):
        self.filePath = filePath
        self.screpPath = screpPath
        self.replaysPath = replaysPath
        self.dbPath = dbPath
        self.status = status

# TODO: This should probably just be in the Settings class itself.
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
        return Settings(filePath=settingsPath, 
                        screpPath=None, 
                        replaysPath=None, 
                        dbPath=None, 
                        status=SettingsStatus.UNINITIALIZED)

    parser.read(settingsPath)

    screpPath = parser["repfinder"]["screp_path"].replace("\"", "").replace("\'", "")
    screpPathRes = Path(screpPath).resolve()
    if not screpPathRes.is_file():
        print(f"screp could not be found. Check if the path is correct in your settings file ('{settingsPath}'):\n'{screpPath}'")
        return Settings(filePath=settingsPath, 
                        screpPath=screpPath, 
                        replaysPath=None, 
                        dbPath=None, 
                        status=SettingsStatus.SCREP_MISSING)

    replaysPath = parser["repfinder"]["replays_folder"].replace("\"", "").replace("\'", "")
    replaysPathRes = Path(replaysPath).resolve()
    if not replaysPathRes.is_dir():
        print(f"The replays folder could not be found. Check if the path is correct in your settings file ('{settingsPath}'):\n'{replaysPath}'")
        return Settings(filePath=settingsPath, 
                        screpPath=screpPathRes, 
                        replaysPath=replaysPath, 
                        dbPath=None, 
                        status=SettingsStatus.REPLAYS_MISSING)
    
    dbPath = parser["repfinder"]["db_folder"].replace("\"", "").replace("\'", "")
    dbPathRes = Path(dbPath).resolve()
    if not dbPathRes.is_dir():
        print(f"The DB folder could not be found. Check if the path is correct in your settings file ('{settingsPath}'):\n'{dbPath}'")
        return Settings(filePath=settingsPath,
                        screpPath=screpPathRes, 
                        replaysPath=replaysPathRes, 
                        dbPath=dbPath, 
                        status=SettingsStatus.DB_MISSING)

    return Settings(filePath=settingsPath, 
                    screpPath=screpPathRes, 
                    replaysPath=replaysPathRes,
                    dbPath=dbPathRes, 
                    status=SettingsStatus.OK)