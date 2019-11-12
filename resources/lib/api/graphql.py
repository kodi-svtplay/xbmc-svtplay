# -*- coding: utf-8 -*-
# system imports
from __future__ import absolute_import,unicode_literals
import json
import re
import requests
from resources.lib import logging

class GraphQL:
    
    def __init__(self):
      pass

    def __get_all_programs(self):
      operation_name = "ProgramsListing"
      query_hash = "1eeb0fb08078393c17658c1a22e7eea3fbaa34bd2667cec91bbc4db8d778580f"
      json_data = self.__get(operation_name, query_hash)
      if not json_data:
        return None # or throw?
      items = []
      for raw_item in json_data["data"]["programAtillO"]["flat"]:
        if raw_item["oppetArkiv"]:
          continue
        title = raw_item["name"]
        url = raw_item["urls"]["svtplay"]
        geo_restricted = raw_item["restrictions"]["onlyAvailableInSweden"]
        item = self.__create_item(title, url, geo_restricted)
        items.append(item)
      return sorted(items, key=lambda item: item["title"])
  
    def getAtoO(self):
      return self.__get_all_programs()

    def getProgramsByLetter(self, letter):
      """
      Returns a list of all program starting with the supplied letter.
      """
      logging.log("getProgramsByLetter: {}".format(letter))
      programs = self.__get_all_programs()
      if not programs:
        return None
      items = []
      pattern = "^[{}]".format(letter.upper())
      for item in programs:
        if re.search(pattern, item["title"]):
          items.append(item)
      return items

    def __create_item(self, title, url, geo_restricted):
      item = {}
      item["title"] = title
      item["url"] = url
      item["thumbnail"] = ""
      item["type"] = "program"
      item["onlyAvailableInSweden"] = geo_restricted
      if "/video/" in item["url"]:
        item["type"] = "video"
      return item

    def __get(self, operation_name, query_hash="", vars = {}):
      base_url = "https://api.svt.se/contento/graphql"
      param_ua = "svtplaywebb-play-render-prod-client"
      ext = {}
      if query_hash:
          ext["persistedQuery"] = {"version":1,"sha256Hash":query_hash}
      query_params = "ua={ua}&operationName={op}&variables={vars}&extensions={ext}"\
        .format(ua=param_ua, op=operation_name, vars=vars, ext=json.dumps(ext, separators=(',', ':')))
      url = "{base}?{query_params}".format(base=base_url, query_params=query_params)
      logging.log("GraphQL request: {}".format(url))
      response = requests.get(url)
      if response.status_code != 200:
        return None
      return response.json()
