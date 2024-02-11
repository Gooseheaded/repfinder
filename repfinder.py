import json
from pathlib import Path
import subprocess
from typing import List
from rfdb import RFDB, AliasAndRace, Replay
from rfsettings import Settings, SettingsStatus
import os
from human_id import generate_id


class Repfinder():
	def __init__(self, settings: Settings, rfdb: RFDB):
		self.settings = settings
		self.db = rfdb
		if settings.status != SettingsStatus.OK:
			raise Exception("Repfinder requires settings to be correct.")


	def syncDb(self):
		successPaths = []
		failurePaths = []
		dirTodos = [self.settings.replaysDirPath]
		while len(dirTodos) > 0:
			for dirTodo in dirTodos:
				print(f"processing replays under {dirTodo}")
				dirTodos.remove(dirTodo)
				for currentDir, dirNames, replayPaths in os.walk(dirTodo):
					# Breadth-first directory search.
					for dirName in dirNames:
						dirNameRes = Path(currentDir, dirName).resolve()
						if not dirNameRes.is_dir():
							# TODO: Log this error; this is suspicious.
							continue
						if dirNameRes not in dirTodos:
							dirTodos.append(dirNameRes)
					# Try and register replays if they do not already exist.
					for replayPath in replayPaths:
						# Encoding the replay name into ascii is a  workaround, to avoid processing
						# replays with names that throw exceptions when used as paths.
						replayPathRes = Path(currentDir, replayPath.encode('ascii', 'ignore').decode()).resolve()
						print(f"Looking at {replayPathRes}")
						if not replayPathRes.is_file():
							# TODO: Log this error; this can be suspicious.
							print(f"(replay) not a file :c")
							continue
						if replayPathRes.suffix.lower() != ".rep":
							continue
						if self.db.readReplay(generate_id(replayPathRes.name)) != None:
							continue
						# A potentially parseable replay that has not been parsed yet!
						if self.registerReplayByPath(replayPathRes):
							successPaths.append(replayPathRes)
						else:
							failurePaths.append(replayPathRes)
		return (successPaths, failurePaths)
	

	def registerReplayByPath(self, replayPath: Path):
		replayPathRes = replayPath
		if not replayPathRes.is_file():
			# TODO: Log this error; this is suspicious.
			return False

		replayJsonStr = subprocess.run(f"{self.settings.screpFilePath} \"{replayPathRes}\"",
									   capture_output=True,
									   shell=True).stdout.decode()

		replayJson = None
		try:
			replayJson = json.loads(replayJsonStr)
		except json.decoder.JSONDecodeError:
			# Replay parsing error.
			# TODO: Log this error.
			return False

		aliasesAndRaces = []
		for player in replayJson["Header"]["Players"]:
			if player["Type"]["Name"] != "Human":
				continue
			if player["Observer"]:
				continue
			aliasesAndRaces.append(AliasAndRace(
				player["Name"], player["Race"]["Name"]))

		# TODO: Verify if these characters are good enough.
		goodChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 1234567890-_.()[]\{\}"
		mapName = "".join(
			char for char in replayJson["Header"]["Map"] if char in goodChars)

		return self.db.createReplay(Replay(replayPathRes, mapName, aliasesAndRaces))

	
	def filterReplaysByAliases(self, replays: dict, aliasesFilter:List[str] = None) -> dict:
		if aliasesFilter is None or len(aliasesFilter) < 1:
			return replays
		
		normAliasesFilter = [alias.lower().strip() for alias in aliasesFilter if len(alias.lower().strip()) > 0]
		results = {}
		for path in replays:
			# Do a friendly comparison between the input alias and the replay aliases
			aliasesFound = 0			
			normReplayAliases = [aliasAndRace.alias.lower().strip() for aliasAndRace in replays[path].aliases]

			for normAliasFilter in normAliasesFilter:
				for normReplayAlias in normReplayAliases:
					# Treat the query alias as a substring, eg. '*alias*'
					if normAliasFilter in normReplayAlias:
						aliasesFound += 1
			
			if aliasesFound == len(normAliasesFilter):
				results[path] = replays[path]
		return results


	def filterReplaysByMapName(self, replays: dict, mapNameFilter:str = '') -> dict:
		results = {}
		if mapNameFilter != '':
			for path in replays:
				# Do a friendly comparison between the input map name and the replay's map name
				normMapNameFilter = mapNameFilter.lower().strip()
				normReplayMapName = replays[path].mapName.lower().strip()

				# Treat the query alias as a substring, eg. '*alias*'
				if normMapNameFilter in normReplayMapName:
					results[path] = replays[path]
		return results
	

	def filterReplaysByRace(self, replays: dict, raceFilter:str = '') -> dict:
		results = {}
		if raceFilter != '':
			for path in replays:
				# Do a friendly comparison between the input race and the replay's player races
				normRaceFilter = raceFilter.lower().strip()
				normReplayRaces = [aliasAndRace.race.lower().strip() for aliasAndRace in replays[path].aliases]

				if normRaceFilter in normReplayRaces:
					results[path] = replays[path]
		return results

	def filterReplaysByLength(self, replays: dict, shorterThan:str, longerThan:str) -> dict:
		# TODO
		pass

	def filterReplaysByLabels(self, replays: dict, labels:List[str]) -> dict:
		# TODO
		pass