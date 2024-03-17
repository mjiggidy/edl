import typing
from timecode import Timecode, TimecodeRange
from . import Event, Track, SourceReel

# TODO: Record list: Using dict with `TimecodeRange` as keys or something?

class RecordEvent:
	"""An EDL consists of record events which reference SFMs and place them in order or something"""

	def __init__(self, event:Event, timecode_record_start:Timecode):
		# TODO: Allow record TC override, or mask certain tracks ("just take video from this VA1V2 thing")?

		self._timecode_record_start = timecode_record_start
		self._source_event:Event = event
	
	@property
	def timecode_extents(self) -> TimecodeRange:
		"""The full extents of this event"""
		return TimecodeRange(start=self._timecode_record_start, duration=self._source_event.duration)
	
	@property
	def duration(self) -> Timecode:
		"""The duraction of this event"""
		return self.timecode_extents.duration # NOTE: Not just passing through the source event duration because of possible FCM mismatch? Think about it or something
	
	@property
	def tracks(self) -> set[Track]:
		"""The track(s) this event affects"""
		return self._source_event.tracks
	
	@property
	def sources(self) -> typing.Iterator[SourceReel]:

		# TODO: This iterates, but source events return a set.  Need to make consistent.
		yield from self._source_event.sources
	
	def __str__(self):
		# TODO: This won't display proper Record TC yet.
		# I think I need to rework Events to do like offsets or something? Ugh.  THINK ABOUT IT.
		return str(self._source_event)