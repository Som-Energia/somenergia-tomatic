import unittest
from execution import (
	Execution,
	executionRoot,
)
from pathlib2 import Path


class Execution_Test(unittest.TestCase):

	def setUp(self):
		self.cleanExecutionDir()
		executionRoot.mkdir()

	def cleanExecutionDir(self):
		def removeRecursive(f):
			if not f.is_dir():
				f.unlink()
				return
			for sub in f.iterdir():
				removeRecursive(sub)
			f.rmdir()
		removeRecursive(executionRoot)

	def listExecutions(self):
		return [
			p.name
			for p in executionRoot.iterdir()
		]

	def test_noExecutions(self):
		self.assertEqual(self.listExecutions(), [
		])

		



