
from __future__ import print_function
import httplib2
import os
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from apiclient import errors
from oauth2client.file import Storage


def insert_comment(service, file_id, content):
  """Insert a new document-level comment.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to insert comment for.
    content: Text content of the comment.
  Returns:
    The inserted comment if successful, None otherwise.
  """
  new_comment = {
      'content': content
  }
  try:
    return service.comments().insert(
        fileId=file_id, body=new_comment).execute()
  except errors.HttpError, error:
    print('An error occurred: %s' % error)
  return None


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    SCOPES = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRET_FILE = '../client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

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

def main(presentationId, comment):
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v2', http=http)
    insertedComment = insert_comment(service, presentationId, comment)

    print(insertedComment)
