import abc, typing, re
from timecode import Timecode, TimecodeRange
from . import SourceReel, Track, Fcm

class StandardFormStatement(abc.ABC):
	"""A base standard form statement"""

	"""
	TODO: CMX3600:
	F1: Event number. Decimal only.  If not decimal, considered note or note statement
	F2: Source. Three-digit reel number (001-253) followed by optional B.  Or BL (Black) or AX (Aux)
	F3: Channels involved A (Audio 1) B (Audio 1 and Video) V (Video) A2 (Audio 2) A2/V (Audio 2 and video) AA (Audio 1 and Audio 2) AA/V (A1/2 & Video)
	F4: Type of edit statement C (cut) D(dissolve), Wxxx (Wipe+CMX wipe code), KB (is the backround of a key), K (is key foreground), KO (is keyed out of the foreground)
	F5: Spaces if C.  001-255 if W, D, or K(?), "(F)" if KB with a fade condition
	F6: Source In
	F7: Source Out
	F8: Record In
	F9: Record Out (Reference only: CMX systems calculate this based on F6-8)

	"""

	def __init__(self, reel_name:str, tracks:typing.Iterable["Track"], timecode_source:TimecodeRange, timecode_record:TimecodeRange, event_number:typing.Optional[int]=None):
		"""Basic parsing of common elements"""
		self._reel = SourceReel.from_string(reel_name)
		self._tracks = tracks
		self._timecode_source = timecode_source
		self._timecode_record = timecode_record
		self._event_number = int(event_number) if event_number is not None else None

	@classmethod
	def all_statement_types(cls) -> typing.Generator["StandardFormStatement", None, None]:
		"""Return all subclasses of this type of statement"""

		for statement in cls.__subclasses__():
			yield from statement.all_statement_types()
			yield statement
	
	@property
	def PAT_EVENT(self) -> re.Pattern:
		"""Regex pattern matching this statement type"""
		pass

	@abc.abstractclassmethod
	def parse_from_pattern(self, statement:re.Pattern) -> "StandardFormStatement":
		"""Create a statement object from a parsed regex object"""
		pass

	@classmethod
	def parse_from_string(cls, line:str) -> "StandardFormStatement":
		"""Create a statement object from a given line from an EDL"""
		pat = cls.PAT_EVENT.match(line)
		if not pat:
			raise ValueError(f"This line is not a valid {cls.__name__}")
		return cls.parse_from_pattern(pat)
	
	@classmethod
	def _parse_shared_elements(cls, statement:re.Pattern) -> typing.Tuple[int, str, typing.Set["Track"], TimecodeRange, TimecodeRange]:

		event_number = int(statement.group("event_number"))
		reel_name = statement.group("reel_name")
		tracks = {Track(statement.group("track_type"))}
		timecode_source = TimecodeRange(
			start=Timecode(statement.group("tc_src_in")), end=Timecode(statement.group("tc_src_out"))
		)
		timecode_record = TimecodeRange(
			start=Timecode(statement.group("tc_rec_in")), end=Timecode(statement.group("tc_rec_out"))
		)

		return event_number, reel_name, tracks, timecode_source, timecode_record
	
	@property
	def source(self) -> SourceReel:
		"""The source reel referenced for this statement"""
		return self._reel

	@property
	def reel_name(self) -> str:
		"""The reel name referenced for this statement"""
		return str(self.source.name)
	
	@property
	def tracks(self) -> typing.Set["Track"]:
		"""The tracks referenced in this statement"""
		return self._tracks
	
	@property
	def timecode_source(self) -> TimecodeRange:
		"""The timecode range used by the source reel"""
		return self._timecode_source
	
	@property
	def timecode_record(self) -> TimecodeRange:
		"""The timecode range the source appears in the timeline"""
		return self._timecode_record
	
	@property
	def event_number(self) -> typing.Union[int,None]:
		"""The original event number from the originating EDL"""
		return self._event_number
	
	@property
	def fcm(self) -> "Fcm":
		"""The Frame Counting Mode for this statement"""
		# TODO: No hardcode no mo plz bb
		return Fcm.NON_DROP_FRAME

class CutStatement(StandardFormStatement):
	"""A simple cut"""

	def __init__(self, reel_name:str, tracks:typing.Iterable["Track"], timecode_source:TimecodeRange, timecode_record:TimecodeRange, event_number:typing.Optional[int]=None):

		super().__init__(
			reel_name=reel_name,
			timecode_source=timecode_source,
			timecode_record=timecode_record,
			tracks=tracks,
			event_number=event_number
		)

	PAT_EVENT = re.compile(
		r"^(?P<event_number>\d+)\s+"
		r"(?P<reel_name>[^\s]+)\s+"
		r"(?P<track_type>A\d*|B|V)\s+"
		r"(?P<event_type>C)\s+"
		r"(?P<tc_src_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_src_out>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_out>\d{2}:\d{2}:\d{2}:\d{2})\s*$"
	, re.I)

	@classmethod
	def parse_from_pattern(cls, statement:re.Pattern) -> "CutStatement":
		"""Create a Cut Statement from a parsed regex string"""

		event_number, reel_name, tracks, timecode_source, timecode_record = super()._parse_shared_elements(statement)

		return cls(
			reel_name = reel_name,
			tracks = tracks,
			timecode_source = timecode_source,
			timecode_record = timecode_record,
			event_number = event_number
		)
	
	def __str__(self):
		# TODO: Additional formatting options (spacing, number padding)
		return f"{str(self.event_number if self.event_number is not None else 1).zfill(3)}  {self.reel_name.ljust(128)}  {str().join(t.name for t in self.tracks).ljust(3)}  C       {self.timecode_source.start} {self.timecode_source.end} {self.timecode_record.start} {self.timecode_record.end}"

class DissolveStatement(StandardFormStatement):
	"""A dissolve statement"""

	PAT_EVENT = re.compile(
		r"^(?P<event_number>\d+)\s+"
		r"(?P<reel_name>[^\s]+)\s+"
		r"(?P<track_type>A\d*|B|V)\s+"
		r"(?P<event_type>D)\s+"
		r"(?P<event_duration>\d+)\s+"
		r"(?P<tc_src_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_src_out>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_out>\d{2}:\d{2}:\d{2}:\d{2})\s*$"
	, re.I)

	def __init__(self, reel_name:str, tracks:typing.Iterable["Track"], timecode_source:TimecodeRange, timecode_record:TimecodeRange, dissolve_length:int, event_number:typing.Optional[int]=None):

		super().__init__(
			reel_name=reel_name,
			timecode_source=timecode_source,
			timecode_record=timecode_record,
			tracks=tracks,
			event_number=event_number
		)

		self._dissolve_length = int(dissolve_length)
	
	@property
	def dissolve_length(self) -> int:
		"""Length in frames of the dissolve"""
		return self._dissolve_length

	@classmethod
	def parse_from_pattern(cls, statement:re.Pattern) -> "DissolveStatement":
		"""Create a Dissolve Statement from a parsed regex string"""

		event_number, reel_name, tracks, timecode_source, timecode_record = super()._parse_shared_elements(statement)

		return cls(
			reel_name = reel_name,
			tracks = tracks,
			dissolve_length = int(statement.group("event_duration")),
			timecode_source = timecode_source,
			timecode_record = timecode_record,
			event_number = event_number
		)

	def __str__(self):
		# TODO: Additional formatting options
		return f"{str(self.event_number if self.event_number is not None else 1).zfill(3)}  {self.reel_name.ljust(128)}  {str().join(t.name for t in self.tracks).ljust(3)}  D  {str(self.dissolve_length).zfill(3)}  {self.timecode_source.start} {self.timecode_source.end} {self.timecode_record.start} {self.timecode_record.end}"

class WipeStatement(StandardFormStatement):
	"""A wipe statement"""

	PAT_EVENT = re.compile(
		r"^(?P<event_number>\d+)\s+"
		r"(?P<reel_name>[^\s]+)\s+"
		r"(?P<track_type>A\d*|B|V)\s+"
		r"(?P<event_type>W\d+)\s+"
		r"(?P<event_duration>\d+)\s+"
		r"(?P<tc_src_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_src_out>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_out>\d{2}:\d{2}:\d{2}:\d{2})\s*$"
	, re.I)

	def __init__(self, reel_name:str, tracks:typing.Iterable["Track"], timecode_source:TimecodeRange, timecode_record:TimecodeRange, wipe_length:int, wipe_id:int, event_number:typing.Optional[int]=None):

		super().__init__(
			reel_name=reel_name,
			timecode_source=timecode_source,
			timecode_record=timecode_record,
			tracks=tracks,
			event_number=event_number
		)

		self._wipe_length = int(wipe_length)
		self._wipe_id     = int(wipe_id)

	@classmethod
	def parse_from_pattern(cls, statement:re.Pattern) -> "WipeStatement":
		"""Create a Dissolve Statement from a parsed regex string"""

		event_number, reel_name, tracks, timecode_source, timecode_record = super()._parse_shared_elements(statement)

		return cls(
			reel_name = reel_name,
			tracks = tracks,
			wipe_length = int(statement.group("event_duration")),
			wipe_id     = int(statement.group("event_type")[1:]),
			timecode_source = timecode_source,
			timecode_record = timecode_record,
			event_number = event_number
		)
	
	@property
	def wipe_length(self) -> int:
		"""Length in frames of the wipe"""
		return self._wipe_length
	
	@property
	def wipe_id(self) -> int:
		"""CMX Wipe ID"""
		return self._wipe_id
	
	def __str__(self):
		# TODO: Additional formatting options
		return f"{str(self.event_number if self.event_number is not None else 1).zfill(3)}  {self.reel_name.ljust(128)}  {str().join(t.name for t in self.tracks).ljust(3)}  W{str(self.wipe_id).zfill(3)}  {str(self.wipe_length).zfill(3)}  {self.timecode_source.start} {self.timecode_source.end} {self.timecode_record.start} {self.timecode_record.end}"

class KeyForegroundStatement(StandardFormStatement):
	"""The edit includes a key"""

	PAT_EVENT = re.compile(
		r"^(?P<event_number>\d+)\s+"
		r"(?P<reel_name>[^\s]+)\s+"
		r"(?P<track_type>A\d*|B|V)\s+"
		r"(?P<event_type>K)\s+"
		r"(?P<event_duration>\d+)\s+"
		r"(?P<tc_src_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_src_out>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_out>\d{2}:\d{2}:\d{2}:\d{2})\s*$"
	, re.I)

	def __init__(self, reel_name:str, tracks:typing.Iterable["Track"], timecode_source:TimecodeRange, timecode_record:TimecodeRange, dissolve_length:int, event_number:typing.Optional[int]=None):

		super().__init__(
			reel_name=reel_name,
			timecode_source=timecode_source,
			timecode_record=timecode_record,
			tracks=tracks,
			event_number=event_number
		)

		self._dissolve_length = int(dissolve_length)
	
	@property
	def dissolve_length(self) -> int:
		"""Length in frames of the dissolve"""
		return self._dissolve_length

	@classmethod
	def parse_from_pattern(cls, statement:re.Pattern) -> "KeyForegroundStatement":
		"""Create a KeyForegroundStatement from a parsed regex string"""

		event_number, reel_name, tracks, timecode_source, timecode_record = super()._parse_shared_elements(statement)

		return cls(
			reel_name = reel_name,
			tracks = tracks,
			dissolve_length = int(statement.group("event_duration")),
			timecode_source = timecode_source,
			timecode_record = timecode_record,
			event_number = event_number
		)

	def __str__(self):
		# TODO: Additional formatting options
		return f"{str(self.event_number if self.event_number is not None else 1).zfill(3)}  {self.reel_name.ljust(128)}  {str().join(t.name for t in self.tracks).ljust(3)}  K  {str(self.dissolve_length).zfill(3)}  {self.timecode_source.start} {self.timecode_source.end} {self.timecode_record.start} {self.timecode_record.end}"
	

class KeyBackgroundStatement(StandardFormStatement):
	"""The edit includes a key"""

	PAT_EVENT = re.compile(
		r"^(?P<event_number>\d+)\s+"
		r"(?P<reel_name>[^\s]+)\s+"
		r"(?P<track_type>A\d*|B|V)\s+"
		r"(?P<event_type>K\s?B)\s+"
		r"(?P<fade_condition>\(F\))?\s+"
		r"(?P<tc_src_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_src_out>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_in>\d{2}:\d{2}:\d{2}:\d{2})\s+"
		r"(?P<tc_rec_out>\d{2}:\d{2}:\d{2}:\d{2})\s*$"
	, re.I)

	def __init__(self, reel_name:str, tracks:typing.Iterable["Track"], timecode_source:TimecodeRange, timecode_record:TimecodeRange, fade_condition:bool, event_number:typing.Optional[int]=None):

		super().__init__(
			reel_name=reel_name,
			timecode_source=timecode_source,
			timecode_record=timecode_record,
			tracks=tracks,
			event_number=event_number
		)

		self._fade_condition = bool(fade_condition)
	
	@property
	def has_fade_condition(self) -> bool:
		"""Length in frames of the dissolve"""
		return self._fade_condition

	@classmethod
	def parse_from_pattern(cls, statement:re.Pattern) -> "KeyBackgroundStatement":
		"""Create a KeyForegroundStatement from a parsed regex string"""

		event_number, reel_name, tracks, timecode_source, timecode_record = super()._parse_shared_elements(statement)

		return cls(
			reel_name = reel_name,
			tracks = tracks,
			fade_condition = bool(statement.group("fade_condition")),
			timecode_source = timecode_source,
			timecode_record = timecode_record,
			event_number = event_number
		)

	def __str__(self):
		# TODO: Additional formatting options
		return f"{str(self.event_number if self.event_number is not None else 1).zfill(3)}  {self.reel_name.ljust(128)}  {str().join(t.name for t in self.tracks).ljust(3)}  K B  {'(F)' if self.has_fade_condition else '   '}  {self.timecode_source.start} {self.timecode_source.end} {self.timecode_record.start} {self.timecode_record.end}"