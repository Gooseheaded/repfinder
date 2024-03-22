import configparser
import platform
from pathlib import Path
from enum import Enum, auto

class SettingsStatus(Enum):
    UNINITIALIZED = auto()
    SCREP_MISSING = auto()
    REPLAYS_MISSING = auto()
    DB_MISSING = auto()
    OK = auto()

class Settings():
    def __init__(self, settingsFilePath: Path, screpFilePath: Path, replaysDirPath: Path, dbDirPath: Path, status: SettingsStatus):
        self.settingsFilePath = settingsFilePath
        self.screpFilePath = screpFilePath
        self.replaysDirPath = replaysDirPath
        self.dbDirPath = dbDirPath
        self.status = status

# TODO: This should probably just be in the Settings class itself.
def init() -> Settings:
    settingsFilePath = Path(Path.cwd(), "repfinder_settings.ini").resolve()
    parser = configparser.ConfigParser()
    defaultScrepFilePath = '"./screp.exe"' if platform.system() == "Windows" else "./screp"

    if not settingsFilePath.is_file():
        parser['repfinder'] = {
            'screp_path': defaultScrepFilePath,
            'replays_folder': 'Your replays folder goes here',
            'db_folder': '"./"',
        }
        with open(settingsFilePath, "w") as settingsFile:
            parser.write(settingsFile)
        print(f"Please edit your settings at '{settingsFilePath}'.")
        return Settings(settingsFilePath=settingsFilePath, 
                        screpFilePath=None, 
                        replaysDirPath=None, 
                        dbDirPath=None, 
                        status=SettingsStatus.UNINITIALIZED)

    parser.read(settingsFilePath)

    screpFilePath = parser["repfinder"]["screp_path"].replace("\"", "").replace("\'", "")
    replaysDirPath = parser["repfinder"]["replays_folder"].replace("\"", "").replace("\'", "")
    dbDirPath = parser["repfinder"]["db_folder"].replace("\"", "").replace("\'", "")

    if screpFilePath == defaultScrepFilePath and replaysDirPath == 'Your replays folder goes here' and dbDirPath == '"./"':
        return Settings(settingsFilePath=settingsFilePath, 
                        screpFilePath=None, 
                        replaysDirPath=None, 
                        dbDirPath=None, 
                        status=SettingsStatus.UNINITIALIZED)

    screpFilePathRes = Path(screpFilePath).resolve()
    if not screpFilePathRes.is_file():
        print(f"screp could not be found. Check if the path is correct in your settings file ('{settingsFilePath}'):\n'{screpFilePath}'")
        return Settings(settingsFilePath=settingsFilePath, 
                        screpFilePath=screpFilePath, 
                        replaysDirPath=None, 
                        dbDirPath=None, 
                        status=SettingsStatus.SCREP_MISSING)

    replaysDirPathRes = Path(replaysDirPath).resolve()
    if not replaysDirPathRes.is_dir():
        print(f"The replays folder could not be found. Check if the path is correct in your settings file ('{settingsFilePath}'):\n'{replaysDirPath}'")
        return Settings(settingsFilePath=settingsFilePath, 
                        screpFilePath=screpFilePathRes, 
                        replaysDirPath=replaysDirPath, 
                        dbDirPath=None, 
                        status=SettingsStatus.REPLAYS_MISSING)
    
    dbDirPathRes = Path(dbDirPath).resolve()
    if not dbDirPathRes.is_dir():
        print(f"The DB folder could not be found. Check if the path is correct in your settings file ('{settingsFilePath}'):\n'{dbDirPath}'")
        return Settings(settingsFilePath=settingsFilePath,
                        screpFilePath=screpFilePathRes, 
                        replaysDirPath=replaysDirPathRes, 
                        dbDirPath=dbDirPath, 
                        status=SettingsStatus.DB_MISSING)

    return Settings(settingsFilePath=settingsFilePath, 
                    screpFilePath=screpFilePathRes, 
                    replaysDirPath=replaysDirPathRes,
                    dbDirPath=dbDirPathRes, 
                    status=SettingsStatus.OK)