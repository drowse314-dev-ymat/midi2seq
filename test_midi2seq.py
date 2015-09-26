# encoding: utf-8

import attest
import iomidi
import midi2seq


conversion = attest.Tests()


class Simple(object):
    pressC = iomidi.NoteOnEvent(
        delta=100,
        channel=0,
        key=60,
        velocity=100)
    releaseC = iomidi.NoteOffEvent(
        delta=100,
        channel=0,
        key=60,
        velocity=0)
    pressD = iomidi.NoteOnEvent(
        delta=100,
        channel=0,
        key=62,
        velocity=100)
    releaseD = iomidi.NoteOffEvent(
        delta=100,
        channel=0,
        key=62,
        velocity=0)
    EOT = iomidi.EndOfTrackEvent(delta=0)
    
    @classmethod
    def midi_beats_track(klass):
        single_track = iomidi.MIDITrack()
        single_track.addEvent(klass.pressC)
        single_track.addEvent(klass.pressD)
        single_track.addEvent(klass.releaseC)
        single_track.addEvent(klass.releaseD)
        single_track.addEvent(klass.pressC)
        single_track.addEvent(klass.releaseC)
        single_track.addEvent(klass.EOT)
    
        return single_track
    
    @classmethod
    def as_beat_seq(klass):
        return [
            klass.beat(time_ms=100, channel=None),
            klass.beat(time_ms=200, channel=None),
            klass.beat(time_ms=500, channel=None),
        ]

    @classmethod
    def as_beat_and_hold_seq(klass):
        return [
            klass.beat(time_ms=100, channel=None),
            klass.holdon(time_ms=200, channel=None),
            klass.holdoff(time_ms=400, channel=None),
            klass.beat(time_ms=500, channel=None),
        ]

    @staticmethod
    def beat(time_ms=0, channel=None):
        return dict(
            type='beat',
            time_ms=time_ms,
            channel=channel)
    @staticmethod
    def holdon(time_ms=0, channel=None):
        return dict(
            type='holdon',
            time_ms=time_ms,
            channel=channel)
    @staticmethod
    def holdoff(time_ms=0, channel=None):
        return dict(
            type='holdoff',
            time_ms=time_ms,
            channel=channel)


@conversion.test
def midi_obj_to_seq_using_default_mapper():
    converter = midi2seq.MIDIConverter()

    assert (
        list(converter.to_seq(
            Simple.midi_beats_track())) ==
        Simple.as_beat_seq())


@conversion.test
def midi_obj_to_seq_using_note_based_mapper():
    def ev_mapper(event):
        if isinstance(event, iomidi.NoteOnEvent):
            if event.key == 60:
                return dict(type='beat')
            elif event.key == 62:
                return dict(type='holdon')
        if isinstance(event, iomidi.NoteOffEvent):
            if event.key == 62:
                return dict(type='holdoff')
        return None
    converter = midi2seq.MIDIConverter(event_mapper=ev_mapper)

    assert (
        list(converter.to_seq(
            Simple.midi_beats_track())) ==
        Simple.as_beat_and_hold_seq())


if __name__ == '__main__':
    tests = attest.Tests([
        conversion
    ])
    tests.run()
