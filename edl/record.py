"""Record timeline... this is #TODO/#TORECONSIDER"""

from timecode import Timecode, TimecodeRange
from . import Event

# TODO: Record list: Using dict with `TimecodeRange` as keys or something?  -- Naaah, not yet at least

# TODO: How to get record TC and event numbers out of source events completely?

class RecordEvent:
	"""An EDL consists of record events which reference SFMs and place them in order or something"""

	def __init__(self, event:Event, timecode_record:TimecodeRange):
		# TODO: Allow record TC override, or mask certain tracks ("just take video from this VA1V2 thing")?

		self._timecode_record = timecode_record
		self._source_event = event
	
	@property
	def timecode_extents(self) -> TimecodeRange:
		"""The full extents of this event"""
		return self._timecode_record
	
	@property
	def duration(self) -> Timecode:
		"""The duraction of this event"""
		return self._timecode_record.duration # NOTE: Not just passing through the source event duration because of possible FCM mismatch? Think about it or something I dunno ugh
	
	@property
	def event(self) -> Event:
		return self._source_event
	
	def __str__(self):
		# TODO: This won't display proper Record TC yet.
		# I think I need to rework Events to do like offsets or something? Ugh.  THINK ABOUT IT.
		return str(self._source_event)