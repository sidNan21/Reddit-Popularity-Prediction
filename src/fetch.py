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

import json
import praw
import src.tools

def fetch_controv_posts(sub, time):
    # read-only reddit client
    reddit = src.tools.redditclient()
    posts = reddit.subreddit(sub).controversial(time)
    return list(posts)


def fetch_top_posts(sub, time):
    # read-only reddit client
    reddit = src.tools.redditclient()
    posts = reddit.subreddit(sub).top(time)
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
def flat_fetch(sub, time, sort='top', num_posts=0, num_comments=0, depth=0):
    # top reddit posts provided target sub and time
    print('fetching posts from {0}...\n \
           sorting by: {1}, scraping {2} posts, {3} comments each (depth={4})' \
           .format(sub, sort, num_posts, num_comments, depth))
    posts = fetch_top_posts(sub, time)[:num_posts]

    # list to build json
    submission_list = list()
    print('serializing data...')
    iteration = 1
    for submission in posts:
        # depth=0: no hierarchy for comments
        # depth=1: 1 child allowed
        # depth=n: n children allowed
        submission.comments.replace_more(limit=depth)
        # organize comment data
        for comment in submission.comments[:num_comments]:
            # basic comment data
            comment_data = {
                'created_utc'   : comment.created_utc,
                'body'          : comment.body,
                'score'         : comment.score,
                'gilds'         : comment.gilded,
                'distinguished' : comment.distinguished,
            }
            submission_list.append(comment_data)
        percent = (iteration * (1+num_comments))/(num_posts + num_posts*num_comments) * 100
        print("percent complete: " + str(percent) + "%")
        iteration += 1

    print('done!')
    # serialize to json
    return submission_list
