# Capstone Data Collection Tool

import os, json, praw, afinn, spacy # pip install afinn spacy praw scipy && python -m spacy download en
from scipy.stats import zscore

def fetch_top_posts(sub, time):
    # read-only reddit client
    print('Connecting to reddit client...')
    reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                         client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                         user_agent='dct user agent')
    posts = reddit.subreddit(sub).top(time)
    print('Connected!')
    return list(posts)

def save_json(submission_list, filename=None):
    # for post in submission_list:
    #     with open('./data/' + post['id'] + '.json', 'w', encoding='utf-8') as f:
    #         json.dump(post, f, ensure_ascii=False, indent=4)
    # print("Saved to data/{0}.json".format(submission_list[0]['id']))
    fn = filename if filename else submission_list[0]['id']
    with open('./data/' + fn + '.json', 'w', encoding='utf-8') as f:
        json.dump(submission_list, f, ensure_ascii=False, indent=4)

def fetch(sub, time, num_posts, num_comments=None):
    # top reddit posts provided target sub and time
    print('Fetching top {0} posts from /r/{1} for time: {2}...'.format(num_posts,sub,time),
          ('' if not num_comments else 'limiting to {0} comments per post'.format(num_comments)))
    posts = fetch_top_posts(sub, time)[:num_posts]
    
    # list to build json
    submission_list = list()
    print('Serializing data...')
    for submission in posts:
        # no hierarchy for comments...
        submission.comments.replace_more(limit=None)
        # basic post data
        submission_data = {
            'id'            : submission.id,
            'title'         : submission.title,
            'created_utc'   : submission.created_utc,
            'body'          : submission.selftext,
            'score'         : submission.score,
            'distinguished' : submission.distinguished
        }
        # organize comment data
        comments = submission.comments.list()
        comments = comments[:num_comments] if num_comments else comments
        comment_list = list()
        for comment in comments:
            # basic comment data
            comment_data = {
                'created_utc'   : comment.created_utc,
                'body'          : comment.body,
                'score'         : comment.score,
                'distinguished' : comment.distinguished,
                'parent'        : comment.parent_id == comment.link_id
            }
            comment_list.append(comment_data)
        # add comment data to submission data
        submission_data['comments'] = comment_list
        # append
        submission_list.append(submission_data)
    
    print('Done!')
    # serialize to json
    return submission_list