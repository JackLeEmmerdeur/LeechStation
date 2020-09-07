from pathlib import Path
from classes import Yaml

LANGS = [
	{
		"name": "english",
		"localename": "English",
		"code": "en"
	},
	{
		"name": "german",
		"localename": "Deutsch",
		"code": "de"
	}
]


class Locale:
	langdir: Path = None
	yaml: Yaml = None

	def __init__(self, langdir: Path):
		self.langdir = langdir
		if not self.langdir.exists():
			raise Exception("Language directory does not exist: '" + str(langdir) + "'")

	def setlang(self, langcode: str) -> bool:
		langset = False
		for lang in LANGS:
			if lang["localename"] == langcode:
				p = self.langdir.joinpath(langcode + ".yaml")
				if p.exists():
					self.yaml = Yaml(p)
				langset = True
		return langset

	def get(self, *propkeychain):
		return self.yaml.get(propkeychain)
