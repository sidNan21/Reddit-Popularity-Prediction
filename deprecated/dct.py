'''
######### DEPRECATED #########
# PLEASE USE fetchbook.ipynb #
##############################

dct.py
    main driver for data collection tool
        capstone research project by Siddharth Nanda and Cory Kim @ UVA
    expects sys args:
        [1] subreddit,
        [2] time,
        [3] number of posts,
        [4]* number of comments,
        [5]* filename
        * = optional
'''

from src import fetch
from src import tools
import time as t
import sys

assert False, "dct.py is deprecated, please use notebooks/fetchbook.ipynb!"

# command line args
# subreddit, time, num_posts = sys.argv[1], sys.argv[2], int(sys.argv[3])
# num_comments = None if len(sys.argv) < 5 else int(sys.argv[4])

# # fetch and save
# timeformat = '%d%m-%H%M'
# filename = '{0}_top{1}{2}_t{3}' \
#                 .format(
#                     subreddit,
#                     num_posts,
#                     time,
#                     t.strftime(timeformat,t.gmtime())
#                 ) if len(sys.argv) < 6 else sys.argv[5]

# submissions = fetch.fetch(sub =          subreddit, 
#                           time =         time, 
#                           num_posts =    num_posts, 
#                           num_comments = num_comments, 
#                           depth =        1)
# tools.save_json(submissions, filename)