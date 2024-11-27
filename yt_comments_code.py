from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

vid_id = input("Enter the YouTube video ID: ")
output_file = input("Enter the output file name: ")

yt_client = build("youtube", "v3", developerKey="AIzaSyCwjAn1wd9uhJji7TXsZPYh4SMlTexcfjY")

def get_comments(client, video_id, token=None):
    try:
        response = client.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            textFormat="plainText",
            maxResults=100,
            pageToken=token
        ).execute()
        return response
    except HttpError as e:
        print(f"HTTP Error: {e.resp.status} - {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

comments = []
next_page_token = None

while True:
    resp = get_comments(yt_client, vid_id, next_page_token)
    
    if not resp:
        break
    
    comments += resp['items']
    next_page_token = resp.get("nextPageToken")
    
    if not next_page_token:
        break

print(f"Total comments fetched: {len(comments)}")

comments_list = []

for item in comments:
    top_comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    comments_list.append({"Comment": top_comment})
    
    if "replies" in item:
        for reply in item["replies"]["comments"]:
            reply_comment = reply["snippet"]["textDisplay"]
            comments_list.append({"Comment": reply_comment})

df = pd.DataFrame(comments_list)

df.to_csv(output_file, index=False, encoding='utf-8')