# Capstone Data Collection Tool

import os, json, sys, praw, afinn, spacy # pip install afinn spacy praw scipy && python -m spacy download en
from scipy.stats import zscore

# Read-only reddit client
reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                     client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                     user_agent='dct user agent')

# Two NLP processors for now because I'm not sure how good spacy's sentiment scoring is
afinn, spacy_nlp = afinn.Afinn(language='en', emoticons=True), spacy.load('en')

# Command line arguments
subreddit, time, num_posts, count = sys.argv[1], sys.argv[2], int(sys.argv[3]), 0

submissionList, submissionScores = list(), list()
submissionTitleSentiments, submissionBodySentiments = list(), list()

# Parse requested number of submissions over requested time period
for submission in reddit.subreddit(subreddit).top(time):
    if count == num_posts: break # Terminate if count reached
    submission.comments.replace_more(limit=None) # No hierarchy for comments, analyze everything with equal importance

    # Save required data from post itself
    top = {'id': submission.id, 'created_utc': submission.created_utc, 'title': submission.title,
    'body': submission.selftext, 'score': submission.score, 'distinguished': submission.distinguished}
    # Save nlp metrics from post itself
    top['title_sentiment'], top['body_sentiment'] = afinn.score(submission.title), afinn.score(submission.selftext)
    entities = spacy_nlp(submission.title).ents
    top['title_entities'] = [{item.label_: item.text} for item in entities]
    entities = spacy_nlp(submission.selftext).ents
    top['body_entities'] = [{item.label_: item.text} for item in entities]
    # Save score and sentiment for z-scores
    submissionScores.append(submission.score)
    submissionTitleSentiments.append(top['title_sentiment'])
    submissionBodySentiments.append(top['body_sentiment'])

    commentList, allScores, allSentiments = list(), list(), list()
    for comment in submission.comments.list():
        # Save required data from every comment
        element = {'created_utc': comment.created_utc, 'body': comment.body,
        'score': comment.score, 'distinguished': comment.distinguished,
        'parent': comment.parent_id == comment.link_id}
        # Save nlp metrics from every comment
        element['sentiment'] = afinn.score(comment.body)
        entities = spacy_nlp(comment.body).ents
        element['entities'] = [{item.label_: item.text} for item in entities]
        # Save score and senitment to calculate z-score later
        allScores.append(comment.score)
        allSentiments.append(element['sentiment'])
        # Save comment to commentList
        commentList.append(element)

    # Calculate z-score for upvotes/sentiment for every comment and add to dict
    z_scores, z_sentiments = zscore(allScores), zscore(allSentiments)
    for element, z_scr, z_snt in zip(commentList, z_scores, z_sentiments):
        element['score_z-score'], element['sentiment_z-score'] = z_scr, z_snt

    # Save post info
    submissionList.append([top, commentList])
    count += 1

# Calculate z-score for upvotes/sentiment of posts relative to other posts (not their comments) and save
z_scores = zscore(submissionScores)
z_title_sentiments, z_body_sentiments = zscore(submissionTitleSentiments), zscore(submissionBodySentiments)
for post, z_scr, z_t, z_b in zip(submissionList, z_scores, z_title_sentiments, z_body_sentiments):
    post[0]['score_z-score'] = z_scr
    post[0]['title_sentiment_z-score'], post[0]['body_sentiment_z-score'] = z_t, z_b

# Serialize to json
for post in submissionList:
    with open('./data/' + post[0]['id'] + '.json', 'w', encoding='utf-8') as f:
        json.dump(post, f, ensure_ascii=False, indent=4)
