# encoding: utf-8

import iomidi


class MIDIConverter(object):

    def __init__(self, event_mapper=None):
        self._event_mapper = self._get_event_mapper(event_mapper)

    def to_seq(self, midi_track):
        accumulated_time_ms = 0
        event_mapper = self._event_mapper

        for event in midi_track.events:
            accumulated_time_ms += event.delta
            event_descriptor = event_mapper(event)

            if event_descriptor is None:
                continue

            yield dict(
                type=event_descriptor['type'],
                channel=event_descriptor.get('channel', None),
                time_ms=accumulated_time_ms)

    def _get_event_mapper(self, user_mapper):
        if user_mapper is not None:
            return user_mapper

        def default_mapper(event):
            if not isinstance(event, iomidi.NoteOnEvent):
                return None
            return dict(type='beat')
        return default_mapper
