import httplib2
import os
import re
import datetime

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import requests
import json

def findPresentationId(url):
    regex = re.findall(r"/presentation/d/([A-Za-z0-9_-]+)/", url)
    return regex[0]

def scrapeTextFromSlides(slides):
    slideText = []
    for i, slide in enumerate(slides):
        pageElem = slide.get('pageElements')
        for element in pageElem:
            try:
                textElems = element["shape"]["text"]["textElements"]
                for x in textElems:
                    if "textRun" in x.keys():
                        slideText.append(x["textRun"]["content"])
            except:
                continue
    return slideText

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
    CLIENT_SECRET_FILE = '../../../client_secret.json'
    APPLICATION_NAME = 'Google Slides API Python Quickstart'
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'slides.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_slides(url):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    slideService = discovery.build('slides', 'v1', http=http)
    presentationId = findPresentationId(url)
    presentation = slideService.presentations().get(
        presentationId=presentationId).execute()

    slides = presentation.get('slides')
    slideText = scrapeTextFromSlides(slides)
    return slideText 
