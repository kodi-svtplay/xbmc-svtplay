import os
import os.path
import sys
import unittest

# Manipulate path to include addon source and stubs
sys.path.append("../")
sys.path.append("./lib")

import resources.lib.helper as helper

DEBUG = True


JSON_GOOD = {
      "video": {
        "videoReferences": [
          {
            "url": "http://bar",
            "bitrate": "0",
            "playerType": "ios"
          }
        ],
        "subtitleReferences": [
          {
            "url": ""
          }
        ]
      }
}
JSON_BAD = {
      "video": {
        "videoReferences": [
          {
            "url": "http://foo",
            "bitrate": "0",
            "playerType": "flash"
          }
        ],
        "subtitleReferences": [
          {
            "url": ""
          }
        ]
      }
}

# Stubbing and patching
class MyFile(file):
  name = "NotSet"
  def __init__(self, name):
    self.name = name
  def close(self):
    pass
  def get_name(self):
    return self.name

def stub_urllib_urlopen(url):
  return myfile(url)

def stub_json_load(file):
  if file.get_name() == "good":
    return JSON_GOOD
  else:
    return JSON_BAD

helper.urllib.urlopen = stub_urllib_urlopen
helper.json.load = stub_json_load

# The real testing begins
class TestHelperModule(unittest.TestCase):

  def test_getVideoUrl(self):
    # Testing a JSON object with an iOS stream
    result = None
    result = helper.getVideoURL(JSON_GOOD)
    self.assertIsNotNone(result)

    # Testing a JSON object without an iOS stream
    result = helper.getVideoURL(JSON_BAD)
    self.assertIsNone(result)



  def test_resolveShowURL(self):
    # Test with a good URL
    show_obj = helper.resolveShowURL("good")
    self.assertIsNotNone(show_obj["videoUrl"])

    show_obj = None

    # Test with a bad URL
    show_obj = helper.resolveShowURL("bad")
    self.assertIsNone(show_obj["videoUrl"])
