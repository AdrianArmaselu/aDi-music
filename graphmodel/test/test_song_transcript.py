import unittest

from graphmodel.appio import reader

class SongTranscriptTest(unittest.TestCase):

  def setUp(self):
    file1 = 'music/mary.mid' 
    self.transcript = reader.load_transcript(file1)

  def test_metadata(self):
    self.assertIsNotNone(self.transcript._transcript_meta)

  def test_notes_sorted_by_time(self):
    for track in self.transcript.get_tracks():
      times = track.times()
      self.assertTrue(all(times[i] <= times[i+1] for i in xrange(len(times)-1)))
