from six import string_types, text_type
from typing import Union, List, Any


def is_string(var: Any) -> bool:
	return isinstance(var, string_types)


def is_unicode(obj: Any) -> bool:
	return isinstance(obj, text_type)


def is_sequence(var: Any) -> bool:
	return (
		not hasattr(var, "strip") and
		hasattr(var, "__getitem__") or
		hasattr(var, "__iter__")
	)


def is_empty_dict(var: dict) -> bool:
	if var is None:
		return True
	a = not isinstance(var, dict)
	b = (len(var) == 0)
	return a and b


def is_empty_sequence(sequencevar: Union[list, set, dict, range, frozenset, tuple, bytearray]) -> bool:
	return not is_sequence(sequencevar) or len(sequencevar) == 0


def string_is_empty(
	thetext: string_types,
	preserve_whitespace: bool=False,
	check_strip_availability: bool=False
) -> bool:
	if thetext is None:
		return True
	isstring = False
	if check_strip_availability:
		isstring = hasattr(thetext, "strip")
	elif is_string(thetext) or is_unicode(thetext):
		isstring = True
	if isstring or isinstance(thetext, bytes):
		return len(thetext if preserve_whitespace else thetext.strip()) < 1
	else:
		return True


def nested_get(dic: dict, keys: List[str]) -> Any:
	"""
	Gets a value from a hierachically organized dict

	Example:
		print(nested_get({"a":{"b":{"c":10}}}, ["a", "b", "c"]))
		>>> 10

	:param dic: The dict of which to get the value for `keys`
	:param keys: A chain of keys
	:return: The value or None if key-chain could not be found
	"""
	if is_empty_dict(dic) or is_empty_sequence(keys):
		return dic
	d = dic
	for key in keys[:-1]:
		if key in d:
			d = d[key]
		else:
			return None
	if keys[-1] in d:
		return d[keys[-1]]
	return None


def nested_set(dic: dict, value: Any, create_missing: bool, keys: List[str]) -> dict:
	"""
	Taken from my answer on
	https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value/49290758#49290758
	Explanation there

	:param dic: A dict of hierachical key-values like {"a":{"b":{"c":1}}}
	:param value: The value you want to set to the key specified with `keys`
	:param create_missing: If False, values of nonexistant keys wont be created
	:param keys: A key-chain (e.g. ["a", "b", "c"])
	:return: The dict-parameter itself for method-chaining
	"""
	if is_empty_dict(dic) or is_empty_sequence(keys):
		return dic

	d = dic
	for key in keys[:-1]:
		if key in d:
			d = d[key]
		elif create_missing:
			d = d.setdefault(key, {})
		else:
			return dic
		if keys[-1] in d or create_missing:
			d[keys[-1]] = value
	return dic