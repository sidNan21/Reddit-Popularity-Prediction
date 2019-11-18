import os
import json
import sys
import praw

reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent='dct user agent')

subreddit, time, num_posts, count = sys.argv[1], sys.argv[2], int(sys.argv[3]), 0

for submission in reddit.subreddit(subreddit).top(time):
    if count == num_posts: break
    submission.comments.replace_more(limit=None)
    submissionList = [comment.body for comment in submission.comments.list()]
    with open(submission.id + '.json', 'w', encoding='utf-8') as f:
        json.dump(submissionList, f, ensure_ascii=False, indent=4)
    count += 1
