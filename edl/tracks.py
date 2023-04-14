import enum, functools

@functools.total_ordering
class Track:
	"""A track containing events in the EDL"""

	tracks = set()

	class Type(enum.Enum):
		"""Types of EDL tracks"""

		VIDEO = "V"
		"""Video track"""

		AUDIO = "A"
		"""Audio track"""

	def __init__(self, name:str):
		"""Create a new EDL track"""

		self._type = self.__class__.Type(name[0].upper())
		self._index = int(name[1:]) if len(name) > 1 else 1
	
	@property
	def name(self) -> str:
		"""The name of the track"""
		if self._index > 1:
			return self._type.value + str(self._index)
		else:
			return self._type.value
	
	@property
	def type(self) -> Type:
		"""The type of data in this EDL track"""
		return self._type
		
	@property
	def track_index(self) -> int:
		"""The track index for the given track type"""
		return self._index
	
	def __eq__(self, other) -> bool:
		if not isinstance(other, self.__class__):
			return False
		return self.name == other.name
	
	def __lt__(self, other) -> bool:
		if not isinstance(other, self.__class__):
			return False
		return self.track_index < other.track_index
	
	def __hash__(self) -> int:
		return hash(self.name)
	
	def __str__(self) -> str:
		return self.name
	
	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} name={self.name}>"