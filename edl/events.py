import typing
from timecode import Timecode, TimecodeRange
from . import StandardFormStatement, NoteFormStatement, SourceReel, Track, Fcm, BaseComment

class Event:
	"""An EDL Event"""

	def __init__(self, standard_statements:typing.Iterable[StandardFormStatement], note_statements:typing.Optional[typing.Iterable["NoteFormStatement"]]=None, comments=typing.Optional[typing.Iterable[BaseComment]]):

		self._sfs = list(standard_statements)
		if not len(self._sfs):
			raise ValueError(f"An event must contain at least one standard form statement (zero were given)")
		self._nfs = note_statements if note_statements else []
		
		fcm = {s.fcm for s in self._sfs}
		if len(fcm) != 1:
			raise ValueError(f"Standard Form Statements must have matching FCMs")
		self._fcm = fcm.pop()

		self._comments = comments if comments else list() # TODO: Temp thing

	@classmethod
	def from_string(cls, event:str) -> "Event":
		"""Parse an event from an event string"""

		sfs = list()
		nfs = list()
		comments = list()

		for line in event.splitlines(keepends=False):
			if not line.strip():
				continue

			parsed = cls._identify_line(line)
			if isinstance(parsed, StandardFormStatement):
				sfs.append(parsed)
			elif isinstance(parsed, NoteFormStatement):
				nfs.append(parsed)
			elif isinstance(parsed, BaseComment):
				comments.append(parsed)
			else:
				raise ValueError(f"Unrecognized line (of type {type(parsed)})in event: {line}")
		
		return cls(
			standard_statements = sfs,
			note_statements = nfs,
			comments = comments
		)
			
	@classmethod
	def _identify_line(cls, line:str) -> typing.Union[StandardFormStatement, NoteFormStatement, str]:
		"""Identify a line"""
		#print(line)
		for s in StandardFormStatement.all_statement_types():
		#	print(s)
			match = s.PAT_EVENT.match(line)
			if match:
				parsed = s.parse_from_pattern(match)
				return parsed

		# Get all weird about it if we didn't recognize a line with an event number at the beginning as an SFM
		if line and line[0].isnumeric():
			raise ValueError(f"Unrecognized standard form statement")

		for n in NoteFormStatement.all_statement_types():
			match = n.PAT_NOTE.match(line)
			if match:
				parsed = n.parse_from_pattern(match)
				return parsed
		
		for c in BaseComment.all_statement_types():
			if c.validate(line):
				return c.from_string(line)
		
		raise ValueError(f"Unrecognized line")

		
	@property
	def tracks(self) -> typing.Set["Track"]:
		"""The track(s) this event belongs to"""
		tracks = set()
		for s in self._sfs:
			for track in s.tracks:
				tracks.add(track)
		return tracks
	
	@property
	def standard_statements(self) -> typing.Generator["StandardFormStatement", None, None]:
		yield from self._sfs

	@property
	def note_statements(self) -> typing.Generator["NoteFormStatement", None, None]:
		yield from self._nfs
	
	@property
	def comments(self) -> typing.Generator[BaseComment, None, None]:
		yield from self._comments
	
	@property
	def sources(self) -> typing.Set[SourceReel]:
		return set(s.source for s in self._sfs)
	
	@property
	def reel_names(self) -> typing.Set[str]:
		return set(s.reel_name for s in self._sfs)
	
	@property
	def timecode_extents(self) -> TimecodeRange:
		"""The full extents of this event"""
		return TimecodeRange(
			start = min(s.timecode_record.start for s in self._sfs),
			end   = max(s.timecode_record.end for s in self._sfs)
		)
	
	@property
	def duration(self) -> Timecode:
		"""The duraction of this event"""
		return self.timecode_extents.duration
	
	@property
	def fcm(self) -> Fcm:
		"""Frame counting mode of this event"""
		return self._fcm
	
	def uses_source(self, source:SourceReel) -> bool:
		"""Does this event reference a given source"""
		return source in self.sources
	
	def __str__(self) -> str:
		# TODO: Add the rest

		return "\n".join([
			"\n".join(str(s) for s in self._sfs),
			"\n".join(str(n) for n in self._nfs),
			"\n".join(str(c) for c in self.comments)
		])