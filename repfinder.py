from pathlib import Path
import configparser
import json
import math
import os # walk
import subprocess
import sys # exit
import time
import webbrowser

if __name__ != "__main__":
	print("[Error] repfinder is meant to be used as a standalone program.")
	sys.exit()

settingsPath = Path(Path.cwd(), "repfinder_settings.ini").resolve()
parser = configparser.ConfigParser()

if not settingsPath.is_file():
	parser['repfinder'] = {
		'screp_path': 'EDIT ME! Copy the path to your screp executable (no quotes needed).',
		'replays_folder': 'EDIT ME! Copy the path to your replays folder (no quotes needed).',
	}
	with open(settingsPath, "w") as settingsFile:
		parser.write(settingsFile)
	print(f"Please edit your settings at '{settingsPath}'.")
	sys.exit()

parser.read(settingsPath)

SCREP_PATH = parser["repfinder"]["screp_path"].replace("\"", "").replace("\'", "")
SCREP_PATH = Path(SCREP_PATH).resolve()
if not SCREP_PATH.is_file():
	print(f"screp could not be found. Check if the path is correct in your settings file ('{settingsPath}'):\n'{SCREP_PATH}'")
	sys.exit()

REPLAYS_FOLDER = parser["repfinder"]["replays_folder"].replace("\"", "").replace("\'", "")
REPLAYS_FOLDER = Path(REPLAYS_FOLDER).resolve()
if not REPLAYS_FOLDER.is_dir():
	print(f"The replays folder could not be found. Check if the path is correct in your settings file ('{settingsPath}'):\n'{REPLAYS_FOLDER}'")
	sys.exit()

if len(sys.argv) < 2:
	print("You must specify the name of the player you are looking for.")
	print("Usage: repfinder.py [name]")
	sys.exit()
LOOKING_FOR_PLAYER = sys.argv[1]

print("                   ___ _           _             ")
print("                  / __|_)         | |            ")
print("  ____ ____ ____ | |__ _ ____   _ | | ____  ____ ")
print(" / ___) _  )  _ \|  __) |  _ \ / || |/ _  )/ ___)")
print("| |  ( (/ /| | | | |  | | | | ( (_| ( (/ /| |    ")
print("|_|   \____) ||_/|_|  |_|_| |_|\____|\____)_|    ")
print("           |_|                                   ")
print("Version 231229.0125\n")
print("Looking for replays...")
print(f"\tstored in '{REPLAYS_FOLDER}'")
print(f"\twith a player called '{LOOKING_FOR_PLAYER}'")
print("")

analyzedCount = 0
matchingReplays = []
startTime = time.monotonic()

for root, dirs, files in os.walk(REPLAYS_FOLDER, topdown=True):
	for name in files:
		replayPath = Path(root, name).resolve()
		if replayPath.suffix != ".rep":
			continue
		if not replayPath.is_file():
			print(f"[Warning] File appears to NOT exist (Path.is_file returned false): {name}")
			continue

		analyzedCount += 1
		singleString = "match" if len(matchingReplays) == 1 else "matches"
		deltaTime = math.floor(time.monotonic() - startTime)
		print(f"({deltaTime}s) Analyzed {analyzedCount} replays so far... ({len(matchingReplays)} {singleString})   ", end="\r")
		replayJsonStr = subprocess.run(f"{SCREP_PATH} \"{replayPath}\"",
								  capture_output=True,
								  shell=True).stdout.decode()

		try:
			replayJson = json.loads(replayJsonStr)
		except json.decoder.JSONDecodeError:
			# Replay parsing error.
			continue
	
		playerData = [player["Name"] for player in replayJson["Header"]["Players"] if player["Type"]["Name"] == "Human" and not player["Observer"]]
		for playerName in playerData:
			if LOOKING_FOR_PLAYER.lower() in playerName.lower():
				matchingReplays.append((replayPath, replayJson))

deltaTime = math.floor(time.monotonic() - startTime)

print("")
if len(matchingReplays) > 1:
	print(f"Found {len(matchingReplays)} matching replays (out of {analyzedCount}) after {deltaTime}s.")
elif len(matchingReplays) == 1:
	print(f"Found a single matching replay (out of {analyzedCount}) after {deltaTime}s.")
else:
	print(f"Found NO matching replays (out of {analyzedCount}) after {deltaTime}s.")
	sys.exit()

# Create the results folder if it does not already exist.
resultsFolder = Path(Path.cwd(), "search_results").resolve()
if not resultsFolder.is_dir():
	os.mkdir(resultsFolder)

# Create the player's results folder if it does not already exist; clears its contents if it does.
playerResultsFolder = Path(resultsFolder, LOOKING_FOR_PLAYER).resolve()
if not playerResultsFolder.is_dir():
	os.mkdir(playerResultsFolder)
else:
	for root, _, files in os.walk(playerResultsFolder):
		for filename in files:
			oldReplayLink = Path(root, filename)
			os.remove(oldReplayLink)

# Create symlinks.
symlinkCounter = 1
for (replayPath, replayJson) in matchingReplays:
	symlinkName = f"{symlinkCounter:03d} "

	playerNames = [player["Name"] for player in replayJson["Header"]["Players"] if player["Type"]["Name"] == "Human" and not player["Observer"]]
	playerRaces = [player["Race"]["Name"][0] for player in replayJson["Header"]["Players"] if player["Type"]["Name"] == "Human" and not player["Observer"]]
	playerSlugs = []
	for idx, name in enumerate(playerNames):
		playerSlugs.append(f"{playerNames[idx]} ({playerRaces[idx]})")
	symlinkName += " vs ".join(playerSlugs)

	goodChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890-_.()[]\{\}"
	mapName = "".join(char for char in replayJson["Header"]["Map"] if char in goodChars)
	symlinkName += f" on {mapName}"

	os.symlink(replayPath, Path(playerResultsFolder, symlinkName))
	symlinkCounter += 1
print(f"Saved shortcuts to the {symlinkCounter-1} replays here: '{playerResultsFolder}'")
input("Press enter to continue.")