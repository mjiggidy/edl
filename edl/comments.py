"""
EDL Comment Types

This represents metadata associated with an event that does not directly affect record length
"""

import abc, re, typing

class BaseComment(abc.ABC):
	"""Base class for a given EDL comment"""

	@classmethod
	def all_statement_types(cls) -> typing.Iterator["BaseComment"]:
		"""Return all subclasses of this type of statement"""

		for statement in cls.__subclasses__():
			yield from statement.all_statement_types()
			yield statement

	@abc.abstractclassmethod
	def from_string(cls, line:str) -> typing.Self:
		"""Parse a comment from a given string"""

	@classmethod
	def validate(cls, line:str) -> bool:
		"""Validate a string input as a valid comment of this type"""

		return all((
			len(line.strip()),
			not re.search("[\n]", line),
			not line.split()[0][0].isnumeric()
		))

class FieldComment(BaseComment):
	"""An EDL comment with a field name and value"""

	# TODO: Marker lists hate it!
	# TODO: Maybe subclass THIS for known types, such as LOC for markers?

	PAT_MATCH = re.compile(r"^\*\s*[^\s]+.*\:\s*[^\s]+.*$")

	def __init__(self, field:str, value:str):
		self._field = field
		self._value = value

	@classmethod
	def validate(cls, line:str) -> bool:
		return all((
			super().validate(line),
			cls.PAT_MATCH.search(line)
		))
	
	@classmethod
	def from_string(cls, line:str) -> typing.Self:

		parsed = line[1:].split(":", maxsplit=1)
		return cls(
			field = parsed[0].strip(),
			value = parsed[1].strip()
		)
	
	@property
	def field(self) -> str:
		"""The field name of the comment"""
		return self._field
	
	@property
	def value(self) -> str:
		"""The value of the comment"""
		return self._value
	
	def __str__(self):
		return f"* {self.field}: {self.value}"
	
class StandardComment(BaseComment):
	"""A standard catch-all EDL comment"""

	def __init__(self, comment:str):
		if not self.validate(comment):
			raise ValueError("This is not a valid comment")
		self._comment = comment

	@classmethod
	def from_string(cls, line:str) -> typing.Self:
		return cls(comment=line)
	
	@classmethod
	def validate(cls, line:str) -> bool:
		"""Is a valid type of StandardComment"""

		return super().validate(line)

	def __str__(self) -> str:
		return self._comment

