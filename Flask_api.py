from flask import Flask, jsonify
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import urllib.parse as p
import re
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

app = Flask(__name__)

@app.route("/")
def youtube_authenticate():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "credentials.json"
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build(api_service_name, api_version, credentials=creds)

# authenticate to YouTube API
youtube = youtube_authenticate()


# In[24]:


def get_video_id_by_url(url):
    """
    Return the Video ID from the video `url`
    """
    # split URL parts
    parsed_url = p.urlparse(url)
    # get the video ID by parsing the query of the URL
    video_id = p.parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    else:
        raise Exception(f"Wasn't able to parse video URL: {url}")


# In[98]:


def get_video_details(youtube, **kwargs):
    return youtube.videos().list(
        part="snippet,contentDetails,statistics",
        **kwargs
    ).execute()

# In[31]:


def search(youtube, **kwargs):
    return youtube.search().list(
        part="snippet",
        **kwargs
    ).execute()


# In[74]:


import pandas as pd   
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-IN')
kw_list = ["Yash Anand"]

def check_trends():
    pytrends.build_payload(kw_list, cat='0', timeframe='now 7-d', geo='IN', gprop='youtube')
    data = pytrends.interest_over_time()
    print(data)


# In[87]:


pytrends.build_payload(kw_list, cat='0', timeframe='now 7-d', geo='IN', gprop='youtube')
related_queries = pytrends.related_queries()
related_queries.values()


# In[95]:


pytrends.build_payload(kw_list=['T-Series'], cat='3', timeframe='today 5-y', geo='IN', gprop='youtube')
related_queries = pytrends.related_queries()
related_queries.values()


# In[97]:


pytrends.build_payload(kw_list=['T-Series'], cat='3', timeframe='today 5-y', geo='IN', gprop='youtube')
pytrends.categories()

if __name__ == "__main__":
    app.run(debug=True)