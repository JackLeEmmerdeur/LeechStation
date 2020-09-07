from lib.helpers import string_is_empty, nested_get, nested_set
from ruamel.yaml import YAML
from typing import Any
from pathlib import Path


class Yaml:

	yaml: YAML = None
	yamlfilepath: Path = None
	yaml_config: Any = None

	def __init__(self, yamlfilepath: Path):
		self.yamlfilepath = yamlfilepath
		with open(str(yamlfilepath), "rt") as yamlfile:
			self.yaml = YAML()
			self.yaml_config = self.yaml.load(yamlfile)

	def get(self, *propkeychain):
		yamlval = nested_get(self.yaml_config, propkeychain)
		if not string_is_empty(yamlval, True):
			yamlval = yamlval.strip()
		return yamlval

	def set(self, value, *propkeychain):
		nested_set(self.yaml_config, value, False, propkeychain)
		with open(str(self.yamlfilepath), "wt") as configfile:
			self.yaml.dump(self.yaml_config, configfile)