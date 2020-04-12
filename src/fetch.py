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
            <float> created_utc,
            <str>   body,
            <int>   score,
            <int>   gilds,
            <str>   distinguished,
        },
        ...
    }
'''
def flat_fetch(sub, time, sort='top', num_posts=0, num_comments=0, depth=0):
    # console message
    print('fetching flat comments from {0}...\
           \nsorting by: {1}, scraping {2} posts, {3} comments each (depth={4})' \
           .format(sub, sort, num_posts, num_comments, depth))
    posts = praw_connect_and_fetch(sub, time, sort)[:num_posts]

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

'''
data {
    comment {
        <int>   id,         (*)
        <int>   parent_id,  (*)
        <bool>  top_level   (*)
        <float> created_utc,
        <str>   body,
        <int>   depth,      (*)
        <int>   score,
        <int>   gilds,
        <str>   distinguished,
    },
    ...
}
'''
def forest_fetch(sub, time, sort='top', num_posts=0, num_comments=None, depth=None):
    # console message
    print('fetching comments from {0}...\
           \nsorting by: {1}, scraping {2} posts' \
           .format(sub, sort, num_posts))
    if num_comments:
        print('hard limit of {0} comments per post...'.format(num_comments))
    if depth:
        print('with maximum comment tree depth of {0}...'.format(depth))
    
    # retrieve posts
    posts = praw_connect_and_fetch(sub, time, sort)[:num_posts]

    res = list()
    depth_map = dict()

    # got messy... starting from scratch
    for p in posts:
        # each post has a hard limit of i < num_comments
        i = 0
        comments = p.comments.list()
        for c in comments:
            # limit reached
            if not num_comments and i == num_comments:
                break
            # is top-level
            if c.parent_id[:3] == 't3_':
                depth_map[c.id] = 0
            # not top-level
            else:
                depth_map[c.id] = depth_map[c.parent_id[3:]]+1
            # enforce depth limit
            if depth and depth_map[c.id] == depth:
                break
            # comment data
            c_dat = {
                'id'            : c.id,
                'parent_id'     : c.parent_id,
                'top_level'     : c.parent_id[:3] == 't3_',
                'created_utc'   : c.created_utc,
                'body'          : c.body,
                'depth'         : depth_map[c.id],
                'score'         : c.score,
                'gilds'         : c.gilded,
                'distinguished' : c.distinguished,
            }
            res.append(c_dat)
            # track progress
            i += 1
            percent = math.floor(i/num_comments)

    # serialize to json
    return res