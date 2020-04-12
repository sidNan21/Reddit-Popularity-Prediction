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
    print('fetching AND flattening comments from {0}...\
           \nsorting by: {1}, scraping {2} posts, {3} comments each (depth={4})' \
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

'''
data {
    comment {
        <int>   id,         (*)
        <int>   parent_id,  (*)
        <bool>  has_parent  (*)
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
def forest_fetch(sub, time, sort='top', num_posts=0, num_comments=0, depth=0):
    # console message
    print('fetching comments from {0}...\
           \nsorting by: {1}, scraping {2} posts, {3} comments each (depth={4})' \
           .format(sub, sort, num_posts, num_comments, depth))
    posts = fetch_top_posts(sub, time)[:num_posts]

    # list to build json
    comment_data = list()
    top_level_comments = list() # will speed-up depth determination
    print('serializing data...')
    i = 1
    for p in posts:
        # depth=0: no hierarchy for comments
        # depth=1: 1 child allowed
        # depth=n: n children allowed
        p.comments.replace_more(limit=depth)
        # organize comment data
        comments = p.comments.list()

        ## TODO: BREAK WHEN NUM_COMMENTS REACHED!!!!

        while comments:
            c = comments.pop(0)
            i += 1
            c_data = {
                'id'            : c.id,
                'parent_id'     : c.parent_id,
                'is_parent'     : len(c.replies) > 0,
                'created_utc'   : c.created_utc,
                'body'          : c.body,
                'depth'         : 0,
                'score'         : c.score,
                'gilds'         : c.gilded,
                'distinguished' : c.distinguished,
            }
            # is a top-level comment
            if (c_data['parent_id'][:3] == 't3_'):
                top_level_comments.append(c_data)
            # append
            comment_data.append(c_data)
            for c_reply in c.replies:
                comments.append(c_reply)

        percent = (i * (1+num_comments))/(num_posts + num_posts*num_comments) * 100
        print("percent complete: " + str(percent) + "%")

    print('done fetching {0} comments'.format(i))
    
    # determine height level of each comment
    res = list()
    comments_queue = list(top_level_comments)
    while comments_queue:
        # get front, check children
        comment = comments_queue.pop(0)
        for c in comments_queue:
            # found a child
            if (comment['id'] == c['parent_id']):
                c['depth'] = comment['depth'] + 1
                # now must check their children
                comments_queue.append(c)
        # append popped comment
        res.append(comment)

    # determine height
    # serialize to json
    return res