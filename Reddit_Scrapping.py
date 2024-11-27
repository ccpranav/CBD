import praw
import pandas as pd
import time

import prawcore

reddit = praw.Reddit(client_id='hF_f2mzIXLOxg1H6rCD83w', 
                     client_secret='UYrDQLvrfUqZBs_CeCz4LXvrY7maiw', 
                     user_agent='scrapper')

subreddit = reddit.subreddit('aww')

comments = []


posts = subreddit.top(time_filter='year', limit=5)

for post in posts:
    try:
        post.comments.replace_more(limit=None)  
        for comment in post.comments.list():
            comments.append(comment.body)
        time.sleep(2) 
    except prawcore.exceptions.TooManyRequests:
        print("Rate limit exceeded. Waiting to retry...")
        time.sleep(60)  
        continue


df = pd.DataFrame(comments, columns=['Comment'])
df.to_csv('reddit_good_comments.csv', mode='a', header=False, index=False)

print("Scraping complete! Comments added to reddit_new_comments.csv")
