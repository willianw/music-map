# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class MusicsItem(scrapy.Item):
    danceability = Field()
    energy = Field()
    key = Field()
    loudness = Field()
    mode = Field()
    speechiness = Field()
    acousticness = Field()
    instrumentalness = Field()
    liveness = Field()
    valence = Field()
    tempo = Field()
    type = Field()
    id = Field()
    uri = Field()
    track_href = Field()
    analysis_url = Field()
    duration_ms = Field()
    time_signature = Field()
    category = Field()
