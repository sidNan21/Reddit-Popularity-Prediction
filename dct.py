import src.fetch as fetch
import time as t
import sys

# command line args
subreddit, time, num_posts = sys.argv[1], sys.argv[2], int(sys.argv[3])
num_comments = None if len(sys.argv) < 5 else int(sys.argv[4])

# fetch and save
timeformat = '%d%m-%H%M'
filename = '{0}_top{1}{2}_t{3}'.format(subreddit, num_posts, time, 
                                       t.strftime(timeformat,t.gmtime()))

submissions = fetch.fetch(subreddit, time, num_posts, num_comments)
fetch.save_json(submissions, filename)