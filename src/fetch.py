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
WIP: going to track comment depth level (by matching parent ids) THEN flatten
'''
def fetch(sub, time, sort='top', num_posts=0, num_comments=0, depth=0):
    # console message
    print('fetching comments from {0}...\
           \nsorting by: {1}, scraping {2} posts, {3} comments each (depth={4})' \
           .format(sub, sort, num_posts, num_comments, depth))
    posts = fetch_top_posts(sub, time)[:num_posts]

    # things will REALLY break if depth < 0... check
    assert depth >= 0, "depth field must be >= 0"

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
        comments = submission.comments.list()[:num_comments]
        submission_data = {
            'id'          : submission.id,
            'created_utc' : submission.created_utc,
            'comments'    : list(),
        }
        for c in comments:
            comment_data = {
                'id'            : c.id,
                'parent_id'     : c.parent_id,
                'created_utc'   : c.created_utc,
                'body'          : c.body,
                'score'         : c.score,
                'gilds'         : c.gilded,
                'distinguished' : c.distinguished,
            }
            submission_data['comments'].append(comment_data)
        submission_list.append(submission_data)
        # for comment in submission.comments[:num_comments]:
        #     # basic comment data
        #     comment_data = {
        #         'created_utc'   : comment.created_utc,
        #         'body'          : comment.body,
        #         'score'         : comment.score,
        #         'gilds'         : comment.gilded,
        #         'distinguished' : comment.distinguished,
        #     }
        #     submission_list.append(comment_data)

        percent = (iteration * (1+num_comments))/(num_posts + num_posts*num_comments) * 100
        print("percent complete: " + str(percent) + "%")
        iteration += 1

    print('done!')
    # serialize to json
    return submission_list