import abc, typing, re
from timecode import Timecode
from . import SourceReel

class NoteFormStatement(abc.ABC):
	"""Note form statement"""

	""""
	TODO: CMX3600:
	FCM:	Frame code mode change (goes before event)
	SPLIT:	Audio/Video split in-time (goes before event) (?)
	GPI		GPI trigger
	M/S		Master/Slave
	SWM		Switcher memory
	M2		Motion memory
	%		Motion memory variable data

	Split examples: (TC is the delay relative to the in-point)
		SPLIT:    AUDIO DELAY=  00:00:00:05
		SPLIT:    VIDEO DELAY=  00:00:02:00
	"""

	@classmethod
	def all_statement_types(cls) -> typing.Generator["NoteFormStatement", None, None]:
		"""Return all subclasses of this type of statement"""

		for statement in cls.__subclasses__():
			yield from statement.all_statement_types()
			yield statement

class MotionMemoryNoteFormStatement(NoteFormStatement):
	"""A motion memory (M2) note form statement"""
	# TODO: Currently supports respeeds but no variable (%) data

	PAT_NOTE = re.compile(
		r"^(?P<note_type>M2)"
		r"\s+"
		r"(?P<reel_name>[^\s]+)"
		r"\s+"
		r"(?P<speed>[\+\-\.0-9]+)\s+"
		r"(?P<tc_src_start>\d{2}:\d{2}:\d{2}:\d{2})\s+"
	, re.I)

	def __init__(self, reel_name:str, speed:float, tc_start:Timecode):
		self._reel = SourceReel.from_string(reel_name)
		self._speed = float(speed)
		self._tc_start = tc_start

	@property
	def source(self) -> SourceReel:
		"""The source reel referenced for this statement"""
		return self._reel

	@property
	def reel_name(self) -> str:
		"""The reel name referenced for this statement"""
		return str(self.source.name)
	
	@property
	def speed(self) -> float:
		"""The speed of the motion"""
		return self._speed
	
	@property
	def timecode_start(self) -> Timecode:
		"""The source start timecode for this respeed"""
		return self._tc_start

	@classmethod
	def parse_from_pattern(cls, statement:re.Pattern) -> "MotionMemoryNoteFormStatement":
		"""Create an M2 note from a parsed regex string"""

		reel_name = statement.group("reel_name")
		speed = float(statement.group("speed"))
		tc_start = Timecode(statement.group("tc_src_start"))

		return cls(
			reel_name=reel_name,
			speed=speed,
			tc_start=tc_start
		)
	
	def __str__(self) -> str:
		return f"M2     {self.reel_name.ljust(129)}  {str(round(self.speed,1)).zfill(6 if self.speed < 0 else 5).rjust(6)}  {self.timecode_start}"

