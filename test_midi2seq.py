# encoding: utf-8

import attest
import iomidi
import midi2seq


conversion = attest.Tests()
utils = attest.Tests()


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
            klass.beat(time_ticks=100, channel=None),
            klass.beat(time_ticks=200, channel=None),
            klass.beat(time_ticks=500, channel=None),
        ]

    @classmethod
    def as_beat_and_hold_seq(klass):
        return [
            klass.beat(time_ticks=100, channel=None),
            klass.holdon(time_ticks=200, channel=None),
            klass.holdoff(time_ticks=400, channel=None),
            klass.beat(time_ticks=500, channel=None),
        ]

    @classmethod
    def as_tone_channeled_seq(klass):
        return [
            klass.beat(time_ticks=100, channel='C'),
            klass.beat(time_ticks=200, channel='D'),
            klass.beat(time_ticks=500, channel='C'),
        ]

    @staticmethod
    def beat(time_ticks=0, channel=None):
        return dict(
            type='beat',
            time_ticks=time_ticks,
            channel=channel)
    @staticmethod
    def holdon(time_ticks=0, channel=None):
        return dict(
            type='holdon',
            time_ticks=time_ticks,
            channel=channel)
    @staticmethod
    def holdoff(time_ticks=0, channel=None):
        return dict(
            type='holdoff',
            time_ticks=time_ticks,
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

@conversion.test
def midi_obj_to_seq_with_channel_mapping():
    converter = midi2seq.MIDIConverter()
    def ev_mapper(event):
        if isinstance(event, iomidi.NoteOnEvent):
            if event.key == 60:
                return dict(type='beat', channel='C')
            elif event.key == 62:
                return dict(type='beat', channel='D')
        return None
    converter = midi2seq.MIDIConverter(event_mapper=ev_mapper)

    assert (
        list(converter.to_seq(
            Simple.midi_beats_track())) ==
        Simple.as_tone_channeled_seq())


@utils.test
def merge_time_sequences():
    seq_a = [
        Simple.beat(time_ticks=100),
        Simple.holdon(time_ticks=200),
        Simple.holdoff(time_ticks=300),
    ]
    seq_b = [
        Simple.beat(time_ticks=150),
        Simple.beat(time_ticks=200),
        Simple.beat(time_ticks=288),
    ]
    assert (
        list(midi2seq.merge_time_sequences(seq_a, seq_b)) ==
        [
            Simple.beat(time_ticks=100),
            Simple.beat(time_ticks=150),
            Simple.holdon(time_ticks=200),
            Simple.beat(time_ticks=200),
            Simple.beat(time_ticks=288),
            Simple.holdoff(time_ticks=300),
        ])


if __name__ == '__main__':
    tests = attest.Tests([
        conversion,
        utils,
    ])
    tests.run()
