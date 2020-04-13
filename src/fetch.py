'''
fetch.py
    simple tool for collection of raw reddit data...
    expects arguments:
        sub  - target subreddit
        time - target time window (e.g. top x posts this week, month, ...)
        num_posts    - limit number of posts
        num_comments - limit number of comments
'''

import json
import praw
import math
import src.tools

def praw_connect_and_fetch(sub, time, sort):
    # check sort type
    assert sort in ('controversial', 'new', 'hot', 'rising', 'top'), \
        'invalid sort-by input, got: '.format(sort)
    # check timeframe
    assert time in ('all', 'day', 'hour', 'month', 'week', 'year'), \
        'invalid time input, got: '.format(time)
    # read-only reddit client
    reddit = src.tools.redditclient()
    subreddit = reddit.subreddit(sub)
    if sort == 'controversial':
        posts = subreddit.controversial(time)
    elif sort == 'new':
        posts = subreddit.new(time)
    elif sort == 'hot':
        posts = subreddit.hot(time)
    elif sort == 'rising':
        posts = subreddit.rising(time)
    elif sort == 'top':
        posts = subreddit.top(time)
    # done
    return list(posts)

'''
formats raw reddit data into serialized jsons with structure:
    data {
        comment {
            <int>   id,
            <int>   parent_id,
            <bool>  top_level,
            <int>   depth,
            <float> created_utc,
            <str>   body,
            <int>   score,
            <int>   gilds,
            <str>   distinguished,
        },
        ...
    }
'''
def fetch(sub, time, sort='top', num_posts=0, num_comments=0, depth=0):
    # console message
    print('fetching comments from {0}...\
           \nsorting by: {1}, scraping {2} posts, {3} comments each (depth={4})' \
           .format(sub, sort, num_posts, num_comments, depth))
    posts = praw_connect_and_fetch(sub, time, sort)[:num_posts]

    # list to build json
    comment_list = list()
    print('serializing data...')
    iteration = 0
    for submission in posts:
        base_time = submission.created_utc
        depth_store, comment_store = dict(), dict()
        # depth=0: no hierarchy for comments
        # depth=1: 1 child allowed
        # depth=n: n children allowed
        submission.comments.replace_more(limit=depth)
        comment_queue = submission.comments[:]  # Seed with top-level
        # organize comment data
        while comment_queue:
            comment = comment_queue.pop(0)
            comment_queue.extend(comment.replies)
            if comment.parent_id[:3] == 't3_':
                depth_store[comment.id] = 0
            else:
                depth_store[comment.id] = depth_store[comment.parent_id[3:]]+1
            comment_data = {
                'id'            : comment.id,
                'parent_id'     : comment.parent_id,
                'top_level'     : comment.parent_id[:3] == 't3_',
                'depth'         : depth_store[comment.id],
                'created_utc'   : comment.created_utc,
                'body'          : comment.body,
                'score'         : comment.score,
                'gilds'         : comment.gilded,
                'distinguished' : comment.distinguished,
            }
            comment_store[comment.id] = comment_data
        '''for _id in comment_store:
            comment = comment_store[_id]
            diff = None
            if comment['parent_id'][:3] == 't3_':
                diff = comment['created_utc'] - base_time
            else:
                diff = comment['created_utc'] - comment_store[comment['parent_id']]['created_utc']
            comment_store[_id]['time_diff'] = diff'''
        comment_list += comment_store.values()
        iteration += 1
        percent = (iteration)/(num_posts) * 100
        print("percent complete: " + str(percent) + "%")

    print('done!')
    # serialize to json
    return comment_list
