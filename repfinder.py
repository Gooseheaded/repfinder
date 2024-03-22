import json
import math
from pathlib import Path
import subprocess
from threading import Thread
from time import sleep
from typing import List
from rfdb import RFDB, AliasAndRace, Replay
from rfsettings import Settings, SettingsStatus
import os
from human_id import generate_id
from queue import Queue

class Repfinder():
	def __init__(self, settings: Settings, rfdb: RFDB):
		if settings.status != SettingsStatus.OK:
			raise Exception("Repfinder requires settings to be correct.")
		self.settings = settings
		self.db = rfdb
		self.replayIndexer = ReplayIndexer()


	def indexReplays(self, targetDirPath:Path=None):
		return self.replayIndexer.startIndexing(self, targetDirPath)
	

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

	def getReplayById(self, replayId:str) -> Replay:
		return self.db.readReplay(replayId)

class ReplayIndexer():
	def __init__(self):
		self.replaysToDoCount = 0
		self.replaysDoneCount = 0
		self.replayPathsToDo = []
		self.isIndexing = False
		self.__thread = Thread()
	
	def startIndexing(self, repfinder, path:Path):
		if self.__thread.is_alive() or self.isIndexing:
			return False

		self.isIndexing = True
		# Estimate work to be done.	
		self.replaysToDoCount = 0
		self.replaysDoneCount = 0
		self.replayPathsToDo = []

		dirTodos = None
		if path is None or not path.is_dir():
			dirTodos = [repfinder.settings.replaysDirPath]
		else:
			dirTodos = [path]

		print("Estimating work.")
		while len(dirTodos) > 0:
			for dirTodo in dirTodos:
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
					# Find unparsed replays.
					for replayPath in replayPaths:
						# Encoding the replay name into ascii is a  workaround, to avoid processing
						# replays with names that throw exceptions when used as paths.
						replayPathRes = Path(currentDir, replayPath.encode('ascii', 'ignore').decode()).resolve()
						if not replayPathRes.is_file():
							# TODO: Log this error; this can be suspicious.
							continue
						if replayPathRes.suffix.lower() != ".rep":
							continue
						replayId = generate_id(seed=replayPathRes.name, word_count=5)
						if repfinder.db.readReplay(replayId) is not None:
							continue
						# A potentially parseable replay that has not been parsed yet!
						print(f"Estimation found replay with id {replayId} which does not exist on db!")
						self.replayPathsToDo.append(replayPathRes)
						self.replaysToDoCount += 1
		print("Estimation done.")
		sleep(5)

		# Do the work.
		self.__thread = Thread(target=self.__indexReplays, args=(repfinder, path,))
		self.__thread.start()
		return True

	def getProgress(self):
		progress = self.replaysDoneCount / self.replaysToDoCount
		if progress == 1:
			self.stopIndexing()
		return self.replaysDoneCount / self.replaysToDoCount

	def stopIndexing(self):
		if not self.__thread.is_alive():
			return False
		self.__thread.join()
		self.isIndexing = False
		return True

	def __indexReplays(self, repfinder:Repfinder, targetDirPath:Path=None):
		if repfinder is None:
			raise Exception("Cannot index replays: Repfinder is required.")

		successPaths = []
		failurePaths = []

		for replayPath in self.replayPathsToDo:
			# The replay name is already encoded here.
			print(f"({self.replaysDoneCount}/{self.replaysToDoCount}) Indexing: {replayPath}")
			if not replayPath.is_file():
				# TODO: Log this error; this can be suspicious.
				continue
			if repfinder.registerReplayByPath(replayPath):
				successPaths.append(replayPath)
			else:
				failurePaths.append(replayPath)
			self.replaysDoneCount += 1
		# NOTE: This return value is currently discarded.
		return (successPaths, failurePaths)
	