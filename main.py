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


# In[99]:


def print_video_infos(video_response):
    items = video_response.get("items")[0]
    # get the snippet, statistics & content details from the video response
    snippet         = items["snippet"]
    statistics      = items["statistics"]
    content_details = items["contentDetails"]
    # get infos from the snippet
    channel_title = snippet["channelTitle"]
    title         = snippet["title"]
    description   = snippet["description"]
    publish_time  = snippet["publishedAt"]
    # get stats infos
    comment_count = statistics["commentCount"]
    like_count    = statistics["likeCount"]
    view_count    = statistics["viewCount"]
    # get duration from content details
    duration = content_details["duration"]
    # duration in the form of something like 'PT5H50M15S'
    # parsing it to be something like '5:50:15'
    parsed_duration = re.search(f"PT(\d+H)?(\d+M)?(\d+S)", duration).groups()
    duration_str = ""
    for d in parsed_duration:
        if d:
            duration_str += f"{d[:-1]}:"
    duration_str = duration_str.strip(":")
    print(f"""    Title: {title}
    Description: {description}
    Channel Title: {channel_title}
    Publish time: {publish_time}
    Duration: {duration_str}
    Number of comments: {comment_count}
    Number of likes: {like_count}
    Number of views: {view_count}
    """)


# In[30]:


video_url = "https://www.youtube.com/watch?v=3K2L7EvQjj4"
# parse video ID from URL
video_id = get_video_id_by_url(video_url)
# make API call to get video info
response = get_video_details(youtube, id=video_id)
# print extracted video infos
print_video_infos(response)


# In[31]:


def search(youtube, **kwargs):
    return youtube.search().list(
        part="snippet",
        **kwargs
    ).execute()


# In[44]:


# search for the query 'python' and retrieve 2 items only
response = search(youtube, q="| DAY 6 | ADVANCE BEGINNER SERIES | Yash Anand", maxResults=10)
items = response.get("items")
for item in items:
    # get the video ID
    video_id = item["id"]["videoId"]
    # get the video details
    video_response = get_video_details(youtube, id=video_id)
    # print the video details
    print_video_infos(video_response)
    print("="*50)


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