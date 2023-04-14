import typing, io
from . import SourceReel, Track, Fcm, Event
	
class Edl:
	"""An Edit Decision List"""

	"""
	TODO:
	Structurally, maybe Edl keeps a list of record TCs and references to Events that only track their local in/out
	"""
	
	def __init__(self, *, title:str="Untitled EDL", fcm:Fcm=Fcm.NON_DROP_FRAME, events:typing.Optional[typing.Iterable[Event]]=None):

		self.title = title
		self.fcm   = fcm
		self._events = list(events) if events else []

	@classmethod
	def from_file(cls, file_edl:io.BufferedReader):
		"""Create an EDL from an input file stream"""
		
		events = []
		event_buffer = []
		current_index = 0

		title = cls._parse_title_from_line(file_edl.readline())
		
		# CMX3600: FCM is not given in the header if PAL
		last_pos = file_edl.tell()
		line_fcm = file_edl.readline()
		if line_fcm.upper().startswith("FCM:"):
			global_fcm = cls._parse_fcm_from_line(line_fcm)
		else:
			global_fcm = Fcm.PAL
			file_edl.seek(last_pos)

		for line_num, line_edl in enumerate(l.rstrip('\n') for l in file_edl.readlines()):

			if not line_edl:
				continue

			try:
				# If starting next event, process event buffer and flush
				if event_buffer and cls._is_begin_new_event(line_edl, current_index):
					events.append(Event.from_string("\n".join(event_buffer)))
					event_buffer=[]
					current_index = 0
				
				# Make note of our current event number if specified
				if line_edl.split()[0].isnumeric():
					current_index=int(line_edl.split()[0])
				
				event_buffer.append(line_edl)

			except Exception as e:
				raise ValueError(f"Line {line_num+2}: {e}")
		
		# Take care of the last little feller.
		# TODO: How to not have to do this?
		if event_buffer:
			events.append(Event.from_string("\n".join(event_buffer)))
		
		return cls(title=title, fcm=global_fcm, events=events)
	
	@staticmethod
	def _is_begin_new_event(line:str, current_index:int) -> bool:
		"""Determine if we're beginning a new event with this line"""

		if not current_index:
			return False

		first_token = line.split(maxsplit=1)[0]
		
		# Encountered prefixed form statement while parsing an event
		if first_token.lower() in {"FCM:","SPLIT:"}:
			return True
		
		# Encountered an event number different than the one we been doin'
		elif first_token.isnumeric() and int(first_token) != current_index:
			return True

		return False

	@staticmethod
	def _parse_title_from_line(line:str) -> str:
		"""Extract a title from a line in an EDL"""
		START = "title:"
		if not line.lower().startswith(START):
			raise ValueError("Title was expected, but not found")
		title = line[len(START):].strip()
		if not len(title):
			raise ValueError("Title is empty")
		return title
	
	@staticmethod
	def _parse_fcm_from_line(line:str) -> Fcm:
		"""Extract the FCM from a line in an EDL"""
		START = "fcm:"
		if not line.lower().startswith(START):
			raise ValueError("FCM was expected, but not found")
		try:
			fcm = Fcm(line[len(START):].strip())
		except:
			raise ValueError("Invalid FCM specified")
		return fcm
	
	def write(self, file:io.TextIOBase):
		"""Write the EDL to a given stream"""

		print(self.header, file=file)
		for event in self.events:
			print(event, file=file)

	@property
	def title(self) -> str:
		"""The title of the EDL"""
		#CMX3600: <=70 chars. Uppercase letters, spaces, numbers only
		return self._title
	
	@title.setter
	def title(self, title:str):
		"""Validate and set the EDL title"""
		
		title = str(title).strip()
		
		if not len(title):
			raise ValueError(f"The title cannot be an empty string")
		
		if len(title.splitlines()) > 1:
			raise ValueError(f"The title must not contain line breaks")
		
		self._title = title

	@property
	def fcm(self) -> Fcm:
		"""The frame counting mode for this EDL"""
		return self._fcm
	
	@fcm.setter
	def fcm(self, fcm:Fcm):
		if not isinstance(fcm, Fcm):
			raise ValueError("Invalid FCM provided")
		self._fcm = fcm

	@property
	def header(self) -> str:
		"""The header for this EDL"""
		
		header = f"TITLE: {self.title}"

		# CMX3600: FCM is excluded from header if PAL
		if self.fcm != Fcm.PAL:
			header += f"\nFCM: {self.fcm.value}"

		return header
	
	@property
	def tracks(self) -> list[Track]:
		"""The tracks used in this EDL"""
		tracks = set()
		for e in self.events:
			tracks = tracks.union(e.tracks)
		return tracks
	
	@property
	def events(self) -> list[Event]:
		"""An EDL event"""
		return self._events
	
	@property
	def sources(self) -> set[SourceReel]:
		"""A set of all sources in the EDL"""
		sources = set()
		for e in self.events:
			sources = sources.union(e.sources)
		return sources
	
	def __str__(self):
		file_text = io.StringIO()
		self.write(file_text)
		return file_text.getvalue()
	
	def __repr__(self):
		return f"<{self.__class__.__name__} title={self.title} FCM={self.fcm} events={len(self.events)}>"