import enum

class Fcm(enum.Enum):
	"""EDL frame counting modes"""
	# TODO: CMX3600: FCM does not appear in PAL systems
	NON_DROP_FRAME = "NON-DROP FRAME"
	DROP_FRAME = "DROP FRAME"
	PAL = "PAL"