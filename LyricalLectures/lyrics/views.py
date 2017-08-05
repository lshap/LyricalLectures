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

def search(request):
    term = "circulate"
    url = "http://api.genius.com/search?q={}".format(term)
    headers = { "Authorization": "Bearer {}".format(GENIUS_ACCESS_TOKEN) }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        try:
            hits = resp.json()['response']['hits']
            if len(hits) >= 1:
                first_hit = hits[0]
                url = first_hit['result']['url']
                lyrics_page = requests.get(url).text
                lyrics_soup = BeautifulSoup(lyrics_page, "html.parser")
                lyrics = lyrics_soup.find("div", "lyrics").find_all("p")
                if len(lyrics):
                    lines = lyrics[0].text.split('\n')
                    searchLyric = [l for l in lines if term.lower() in l.lower()][0]
                    return HttpResponse(searchLyric)
                else:
                    return HttpResponse("No lyrics were found")
            else:
                return HttpResponse("No results were found")
        except ValueError:
            return HttpResponse("Could not parse json from response: {}".format(resp.text))
    else:
        return HttpResponse("There was an error searching the genius api: {}".format(resp.text))
        print resp.text


