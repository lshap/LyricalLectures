# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import requests
from bs4 import BeautifulSoup
import json
from LyricalLectures.settings import GENIUS_ACCESS_TOKEN
from nltk import word_tokenize, pos_tag

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

def find_lyrics_for_verb(verb):
    url = "http://api.genius.com/search?q={}".format(verb)
    headers = { "Authorization": "Bearer {}".format(GENIUS_ACCESS_TOKEN) }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        try:
            hits = resp.json()['response']['hits']
            if len(hits) >= 1:
                lyric_resp = find_first_lyric(hits[:5], verb)
                return lyric_resp
            else:
                return "No results were found"
        except ValueError:
            return "Could not parse json from response: {}".format(resp.text)

@csrf_exempt
def search(request):
    if request.method == "POST":
        body = json.loads(request.body)
        slide_lyrics = []
        for slide in body['slides']:
            tagged_sentence = pos_tag(word_tokenize(slide))
            verbs = [w for w in tagged_sentence if w[1].startswith("VB")]
            print verbs
            verbs.sort(lambda x,y: cmp(len(x[1]), len(y[1])))
            print verbs
            verbs = [v[0] for v in verbs]
            if len(verbs):
                lyric = find_lyrics_for_verb(verbs[0])
                slide_lyrics.append(lyric)
            else:
                print "No verb found for this slide"
        return HttpResponse(json.dumps({"lyrics": slide_lyrics}, indent=2))

