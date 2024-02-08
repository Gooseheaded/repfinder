import json
from pathlib import Path
import subprocess
from rfdb import RFDB, AliasAndRace, Replay
from rfsettings import Settings, SettingsStatus
import os


class Repfinder():
	def __init__(self, settings: Settings, rfdb: RFDB):
		self.settings = settings
		self.db = rfdb
		if settings.status != SettingsStatus.OK:
			raise Exception("Repfinder requires settings to be correct.")

	def syncDb(self):
		successPaths = []
		failurePaths = []
		dirTodos = [self.settings.replaysPath]
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
						replayPathRes = Path(currentDir, replayPath).resolve()
						print(f"(replay) Could be: {replayPath}")
						if not replayPathRes.is_file():
							# TODO: Log this error; this is suspicious.
							print(f"(replay) not a file :c")
							continue
						if replayPathRes.suffix.lower() != ".rep":
							print(f"(replay) not a replay :c")
							continue
						if self.db.readReplay(replayPathRes) != None:
							print(f"(replay) already exists :c")
							continue
						# Things get interesting.
						print(f"aw yes bayybyyy: {replayPathRes}")
						if self.registerReplay(replayPathRes):
							successPaths.append(replayPathRes)
						else:
							failurePaths.append(replayPathRes)
		return (successPaths, failurePaths)
	

	def registerReplay(self, replayPath: Path):
		replayPathRes = replayPath
		if not replayPathRes.is_file():
			# TODO: Log this error; this is suspicious.
			return False

		replayJsonStr = subprocess.run(f"{self.settings.screpPath} \"{replayPathRes}\"",
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
