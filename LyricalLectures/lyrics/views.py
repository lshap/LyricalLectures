# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

import requests
from bs4 import BeautifulSoup
import json
from LyricalLectures.settings import GENIUS_ACCESS_TOKEN

def replace_with_newlines(element):
    text = ''
    for elem in element.recursiveChildGenerator():
        if isinstance(elem, types.StringTypes):
            text += elem.strip()
        elif elem.name == 'br':
            text += '\n'
    return text

def find_first_lyric(hits, term):
    found_lyrics = []
    print len(hits)
    for hit_result in hits:
        hit = hit_result['result']
        artist =  hit['primary_artist']['name']
        title = hit["title"]
        lyrics_page = requests.get(hit['url']).text
        lyrics_soup = BeautifulSoup(lyrics_page, "html.parser")
        lyrics = lyrics_soup.find("div", "lyrics").find_all("p")
        if len(lyrics):
            lines = lyrics[0].text.split('\n')
            searchLyrics = [l for l in lines if term.lower() in l.lower()]
            if len(searchLyrics) >=1:
                found_lyrics.append("Just like {} said in {}: \"{}\"" \
                    .format(artist, title, searchLyrics[0]))
    if len(found_lyrics):
        return max(found_lyrics, key=len)
    else:
        return "No result was found"

def search(request):
    term = "choose"
    url = "http://api.genius.com/search?q={}".format(term)
    headers = { "Authorization": "Bearer {}".format(GENIUS_ACCESS_TOKEN) }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        try:
            hits = resp.json()['response']['hits']
            if len(hits) >= 1:
                lyric_resp = find_first_lyric(hits[:5], term)
                return HttpResponse(lyric_resp)
            else:
                return HttpResponse("No results were found")
        except ValueError:
            return HttpResponse("Could not parse json from response: {}".format(resp.text))
    else:
        return HttpResponse("There was an error searching the genius api: {}".format(resp.text))
        print resp.text


