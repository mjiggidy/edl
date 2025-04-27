import sys
import edl
from rich.console import Console
from rich.text import Text
from rich.style import Style


def events_match(event_source:edl.events.Event, event_compare:edl.events.Event) -> bool:
	"""Should match source set and record TC I guess"""

	return all([
		{s.name.lower() for s in event_source.sources} == {s.name.lower() for s in event_compare.sources},
		event_source.timecode_extents == event_compare.timecode_extents
	])

def formatted_event(event:edl.events.Event) -> str:

	return f"{event.event_number}: {[f'{s.source}' for s in event.standard_statements]}   {event.timecode_extents}"

if __name__ == "__main__":

	console = Console(highlight=False)
	style_warning = Style(bgcolor="yellow")
	style_matched = Style(bgcolor="green")
	style_nomatch = Style(bgcolor="red")

	if len(sys.argv) < 3:
		sys.exit(f"Usage: {__file__} list1.edl list2.edl")
	
	try:
		with open(sys.argv[1]) as edl1:
			edl_source = edl.Edl.from_stream(edl1)
	
		with open(sys.argv[2]) as edl2:
			edl_comp = edl.Edl.from_stream(edl2)
	
	except Exception as e:
		sys.exit(f"Trouble parsing EDL: {e}")

	print(f"Comparing source EDL {edl_source.title} against {edl_comp.title}")

	matched_events = []
	unmatched_events = []
	skipped_events = []

	source_events = iter(edl_source.events)
	compare_events = iter(edl_comp._events)

	event_source = next(source_events)
	event_compare = next(compare_events)

	while event_source and event_compare:


		while event_source.timecode_extents.start != event_compare.timecode_extents.start:

			console.print("")

			# If no longer tracking record TC, try to catch up
			if event_source.timecode_extents.start < event_compare.timecode_extents.start:
				skipped_events.append(event_source)
				console.print(Text("Skipping source event: ", style=style_warning))
				console.print(Text(formatted_event(event_source)))
				event_source = next(source_events)
			else:
				skipped_events.append(event_compare)
				console.print(Text("Skipping compared event: ", style=style_warning))
				console.print(formatted_event(event_compare))
				event_compare = next(compare_events)

		console.print("")

		if events_match(event_source, event_compare):
			matched_events.append(event_source)
			console.print(Text("Matched:", style=style_matched))
		
		else:
			unmatched_events.append(event_source)
			console.print(Text("Not matched:", style=style_nomatch))

		console.print(formatted_event(event_source))
		console.print(formatted_event(event_compare))

		try:
			event_source = next(source_events)
			event_compare = next(compare_events)
		except StopIteration:
			break

		

		
	console.print("")
	console.print(f"{len(matched_events)} matched; {len(unmatched_events)} not matched; {len(skipped_events)} skipped")