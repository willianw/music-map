# -*- coding: utf-8 -*-

from scrapy import Request
from scrapy.shell import inspect_response
from urllib.parse import urlencode, quote

import requests
import scrapy
import base64
import json
import pdb
import os

from musics.items import MusicsItem

SPOTIFY_CLIENT = os.environ['SPOTIFY_CLIENT']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']


class SpotifySpider(scrapy.Spider):
    name = 'spotify'
    allowed_domains = ['api.spotify.com', 'accounts.spotify.com']

    def start_requests(self):
        base_url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Accept': "application/json",
            'User-Agent': 'python-requests/2.22.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(
                base64.b64encode('{}:{}'.format(
                    SPOTIFY_CLIENT, SPOTIFY_SECRET
                ).encode()).decode()
            )
        }
        payload = {'grant_type': 'client_credentials'}
        yield Request(base_url, self.parse_auth, method='POST',
                      headers=headers, body=urlencode(payload))

    def parse_auth(self, response):
        credentials = json.loads(response.body_as_unicode())
        self.token = credentials['access_token']
        print(self.token)
        base_url = 'https://api.spotify.com/v1/recommendations/' \
                   + 'available-genre-seeds'
        headers = {
            'Authorization': f"Bearer {self.token}",
            'Accept': "application/json",
            'Content-Type': "application/json",
            'cache-control': "no-cache",
        }
        yield Request(base_url, self.parse_categories, headers=headers)

    def parse_categories(self, response):
        base_url = 'https://api.spotify.com/v1/browse/categories/{}/playlists'
        genres = json.loads(response.body_as_unicode())['genres']
        for genre in genres:
            yield Request(base_url.format(genre), method='GET',
                          callback=self.parse_playlists,
                          headers=response.request.headers,
                          meta={'genre': genre})
    
    def parse_playlists(self, response):
        body = json.loads(response.body_as_unicode())['playlists']
        next_page = body['next']
        if next_page:
            yield Request(next_page, method='GET',
                          callback=self.parse_playlists,
                          headers=response.request.headers,
                          meta=response.meta)
        for playlist in body['items']:
            tracks_url = playlist['tracks']['href']
            yield Request(tracks_url, method='GET',
                          callback=self.parse_playlist,
                          headers=response.request.headers,
                          meta=response.meta)

    def parse_playlist(self, response):
        track_features = 'https://api.spotify.com/v1/audio-features?ids={}'
        body = json.loads(response.body_as_unicode())
        next_page = body['next']
        if next_page:
            yield Request(next_page, method='GET',
                          callback=self.parse_playlist,
                          headers=response.request.headers,
                          meta=response.meta)
        playlist_track_ids = [
            track['track']['id']
            for track in body['items']
        ]
        track_ids = quote(','.join(playlist_track_ids))
        yield Request(track_features.format(track_ids), method='GET',
                      callback=self.parse_tracks, meta=response.meta,
                      headers=response.request.headers)

    def parse_tracks(self, response):
        musics = json.loads(response.body_as_unicode())['audio_features']
        for item in musics:
            music = MusicsItem(item)
            music['genre'] = response.meta['genre']
            yield music
