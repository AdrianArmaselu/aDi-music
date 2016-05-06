import unittest

from graphmodel.appio import reader

class SongTranscriptTest(unittest.TestCase):

  def setUp(self):
    file1 = '../music/mary.mid' 
    self.transcript = reader.load_transcript(file1)

  def test_metadata(self):
    self.assertIsNotNone(self.transcript._transcript_meta)

  def test_notes_sorted_by_time(self):
    for track in self.transcript.get_tracks():
      times = track.times()
      self.is_sorted(times)

  def test_merge_tracks(self):
    f = 'music/bach.mid'
    transcript2 = reader.load_transcript(f)
    # TODO: finish here
    # self.is_merged(self.transcript.get_track(??), transcript2.get_track(??), ??)

  def is_merged(self, track1, track2, merged):
    self.is_sorted(merged.times())
    merged_sound_events = merged.get_sound_events()
    for sound_event in track1.get_sound_events():
      self.assertIn(sound_event, merged_sound_events)
    for sound_event in track2.get_sound_events():
      self.assertIn(sound_event, merged_sound_events)


  def is_sorted(self, array):
    self.assertTrue(all(array[i] <= array[i+1] for i in xrange(len(array)-1)))

