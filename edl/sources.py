import abc, re

class SourceReel(abc.ABC):
	"""A base source for use as a reel name in a Standard Form Statement"""

	@property
	def _NAME(self) -> str:
		pass

	@property
	def name(self) -> str:
		"""The source reel name"""
		return self._NAME
	
	def __str__(self):
		return self.name
	
	def __eq__(self, other):
		return self.name == other.name
	
	def __hash__(self):
		return hash(self._NAME)
	
	@classmethod
	def from_string(cls, reel_name:str):

		if BlackSource.validate(reel_name):
			return BlackSource()
		elif AuxSource.validate(reel_name):
			return AuxSource()
		elif TapeSource.validate(reel_name):
			return TapeSource(reel_name)
		else:
			raise ValueError("Reel name format is not recognized")

class BlackSource(SourceReel):
	"""A black/empty source"""

	_NAME = "BL"

	@classmethod
	def validate(self, reel_name:str) -> bool:
		"""Is this a valid Black source"""
		return reel_name.upper() == "BL"

class AuxSource(SourceReel):
	"""An auxillary source"""

	_NAME = "AX"

	@classmethod
	def validate(self, reel_name:str) -> bool:
		return reel_name.upper() == "AX"

class Master (SourceReel):
	""""""

	_NAME = "MSTR"



class TapeSource(SourceReel):

	_NAME = str()

	def __init__(self, reel_name:str):

		if not self.validate(reel_name):
			raise ValueError(f"Reel name contains invalid characters for this source type")

		super().__init__()
		self._NAME = reel_name

	@classmethod
	def validate(cls, reel_name:str) -> bool:
		# TODO: CMX3600: Special characters except comma (,) and space ( ) can occur within reel names
		return len(reel_name.strip()) and not re.search("[\s]", reel_name)