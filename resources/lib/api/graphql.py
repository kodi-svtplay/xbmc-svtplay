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

    def getGenres(self):
      operation_name = "AllGenres"
      query_hash = "6bef51146d05b427fba78f326453127f7601188e46038c9a5c7b9c2649d4719c"
      json_data = self.__get(operation_name, query_hash)
      if not json_data:
        return None
      genres = []
      for item in json_data["data"]["genresSortedByName"]["genres"]:
        genre = {}
        genre["title"] = item["name"]
        genre["genre"] = item["id"]
        genres.append(genre)
      return genres

    def getProgramsForGenre(self, genre):
      operation_name = "GenreProgramsAO"
      query_hash = "189b3613ec93e869feace9a379cca47d8b68b97b3f53c04163769dcffa509318"
      variables = {"genre":[genre]}
      json_data = self.__get(operation_name, query_hash, variables=variables)
      if not json_data:
        return None
      raw_items = []
      for selection in json_data["data"]["genres"][0]["selectionsForWeb"]:
        if selection["id"] == "all-{}".format(genre):
          raw_items = selection
          break
      programs = []
      for item in raw_items["items"]:
        item = item["item"]
        title = item["name"]
        url = item["urls"]["svtplay"]
        plot = item["longDescription"]
        programs.append({
          "title": title,
          "url": url,
          "thumbnail": "",
          "info": {"plot": plot},
          "type" : "video" if item["__typename"] == "Single" else "program",
          "onlyAvailableInSweden" : item["restrictions"]["onlyAvailableInSweden"],
          "inappropriateForChildren" : False
        })
      return programs
    
    def getEpisodes(self, slug):
      operation_name = "TitlePage"
      query_hash = "4122efcb63970216e0cfb8abb25b74d1ba2bb7e780f438bbee19d92230d491c5"
      variables = {"titleSlugs":[slug]}
      json_data = self.__get(operation_name, query_hash, variables=variables)
      if not json_data:
        return None
      if not json_data["data"]["listablesBySlug"]:
        return None
      episodes = []
      inappropriate_for_children = json_data["data"]["listablesBySlug"][0]
      for content in json_data["data"]["listablesBySlug"][0]["associatedContent"]:
        if content["id"] == "upcoming":
          continue
        for item in content["items"]:
          episode = {}
          item = item["item"]
          episode["title"] = item["name"]
          episode["url"] = item["urls"]["svtplay"]
          episode["onlyAvailableInSweden"] = item["restrictions"]["onlyAvailableInSweden"]
          episode["inappropriateForChildren"] = inappropriate_for_children
          episode["type"] = "video"
          episode["thumbnail"] = ""
          info = {}
          info["plot"] = item["longDescription"]
          info["duration"] = item.get("duration", 0)
          episode["info"] = info
          episodes.append(episode)
      return episodes

    def getLatestNews(self):
      operation_name = "GenreLists"
      query_hash = "90dca0b51b57904ccc59a418332e43e17db21c93a2346d1c73e05583a9aa598c"
      variables = {"genre":["nyheter"]}
      genre = "nyheter"
      json_data = self.__get(operation_name, query_hash, variables=variables)
      if not json_data or not json_data["data"]["genres"]:
        return None
      raw_items = []
      if not json_data["data"]["genres"][0]["selectionsForWeb"]:
        return None
      for selection in json_data["data"]["genres"][0]["selectionsForWeb"]:
        if selection["id"] != "latest-{}".format(genre):
          continue
        raw_items = selection["items"]
      latest_news = []
      for item in raw_items:
        title = "{heading} - {subHeading}".format(heading=item["heading"], subHeading=item["subHeading"])
        item = item["item"]
        episode = {}
        episode["title"] = title
        episode["url"] = item["urls"]["svtplay"]
        episode["thumbnail"] = ""
        episode["inappropriateForChildren"] = False
        episode["onlyAvailableInSweden"] = item["restrictions"].get("onlyAvailableInSweden", False)
        info = {}
        info["duration"] = item["duration"]
        episode["info"] = info
        latest_news.append(episode)
      return latest_news
      
    def __get(self, operation_name, query_hash="", variables = {}):
      base_url = "https://api.svt.se/contento/graphql"
      param_ua = "svtplaywebb-play-render-prod-client"
      ext = {}
      if query_hash:
          ext["persistedQuery"] = {"version":1,"sha256Hash":query_hash}
      query_params = "ua={ua}&operationName={op}&variables={variables}&extensions={ext}"\
        .format(ua=param_ua, op=operation_name, variables=json.dumps(variables, separators=(',', ':')), ext=json.dumps(ext, separators=(',', ':')))
      url = "{base}?{query_params}".format(base=base_url, query_params=query_params)
      logging.log("GraphQL request: {}".format(url))
      response = requests.get(url)
      if response.status_code != 200:
        logging.error("Request failed, code: {code} url: {url}".format(code=response.status_code, url=url))
        return None
      return response.json()
