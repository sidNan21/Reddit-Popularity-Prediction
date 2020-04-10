'''
fetch.py
    simple tool for collection of raw reddit data...
    expects arguments:
        sub  - target subreddit
        time - target time window (e.g. top x posts this week, month, ...)
        num_posts    - limit number of posts
        num_comments - limit number of comments
    saves into a json file with simple naming convention:
        {subreddit}_top{num_posts}{time}_t{ddmm-HHMM}.json
'''

import os
import json
import praw

def fetch_top_posts(sub, time):
    # read-only reddit client
    print('Connecting to reddit client...')
    reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                         client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                         user_agent='dct user agent')
    posts = reddit.subreddit(sub).top(time)
    print('Connected!')
    return list(posts)

'''
formats raw reddit data into serialized jsons with structure:
    data {
            [
                submission {
                    <str>   id,
                    <str>   title,
                    <float> created_utc,
                    <str>   body,
                    <int>   score,
                    <str> distinguished,
                    comments [
                        comment {
                            <float> created_utc,
                            <str>   body,
                            <int>   score,
                            <str>   distinguished,
                            <bool>  parent
                        }
                        ..
                    ]
                }
                ..
            ]
    }
'''
def fetch(sub, time, num_posts, num_comments=None):
    # top reddit posts provided target sub and time
    print('fetching top {0} posts from /r/{1} for time: {2}...'.format(num_posts,sub,time),
          ('' if not num_comments else 'limiting to {0} comments per post'.format(num_comments)))
    posts = fetch_top_posts(sub, time)[:num_posts]

    # list to build json
    submission_list = list()
    print('serializing data...')
    iteration = 1
    for submission in posts:
        # no hierarchy for comments...
        submission.comments.replace_more(limit=3)
        # basic post data
        submission_data = {
            'created_utc'   : submission.created_utc,
            'body'          : submission.title + "\n" + submission.selftext,
            'score'         : submission.score,
            'distinguished' : submission.distinguished,
            'post'          : True,
        }
        submission_list.append(submission_data)
        # organize comment data
        for comment in submission.comments[:num_comments]:
            # basic comment data
            comment_data = {
                'created_utc'   : comment.created_utc,
                'body'          : comment.body,
                'score'         : comment.score,
                'distinguished' : comment.distinguished,
                'post'          : False,
            }
            submission_list.append(comment_data)
        percent = (iteration * (1+num_comments))/(num_posts + num_posts*num_comments) * 100
        print("Percent Complete: " + str(percent) + "%")
        iteration += 1

    print('done!')
    # serialize to json
    return submission_list
