
from __future__ import print_function
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

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/slides.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/presentations.readonly'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Google Slides API Python Quickstart'

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

    if len(slideText) > 0:
        writeToTextFile(slideText)
    return slideText

def writeToTextFile(text):
    timeNow = datetime.datetime.now().strftime("%Y-%m-%d(%H:%M:%S)")
    textfile = open('%s.txt'%timeNow, 'w')
    for text in text:
        textfile.write(text.encode('ascii', 'ignore'))
    textfile.close()


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
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


def main():
    """Shows basic usage of the Slides API.

    Creates a Slides API service object and prints the number of slides and
    elements in a sample presentation:
    https://docs.google.com/presentation/d/1EAYk18WDjIG-zp_0vLm3CsfQh_i8eXc67Jo2O9C6Vuc/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('slides', 'v1', http=http)

    presentationId = '19A4iCEHvXvLcgH5ugmQEHQfCRmqyPMS4Oy-kpXNXy8E'
    presentation = service.presentations().get(
        presentationId=presentationId).execute()


    slides = presentation.get('slides')
    slideText = scrapeTextFromSlides(slides)
    data = { "slides": slideText }
    resp = requests.post("http://localhost:8000/lyricize/", data=json.dumps(data))
    print(resp.text)

if __name__ == '__main__':
    main()
