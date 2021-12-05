import csv
from datetime import datetime
import numpy as np #Primarily used for data storage and organization before conversion to a dataframe
import pandas as pd #Library used to store data in csv compatable files known as dataframes
import praw #Library used for web-scrapping data from Reddit
from nltk.tokenize import sent_tokenize
from nltk.tag import pos_tag
import text2emotion as te
##Submission Statics
#Static variables for naming columns obtained for submissions
SUBMISSION_CSV = "submissions.csv"
SUB_TITLE = "body"
SUB_AUTHOR = "Author"
SUB_CREATED = "timestamp"
SUB_DISTINGUISHED = "Distinguished"
SUB_EDITED = "Edited"
SUB_ID = "Id"
SUB_LOCKED = "Locked"
SUB_NAME = "Name"
SUB_NUMCOM = "Num Comments"
SUB_SCORE = "num_upvotes"
SUB_UPVOTE_RATIO = "Upvote Ratio"

##Comment Statics
#Static variables for naming columns obtained for submission comments
COMMENTS_CSV = "comments.csv"
COMMENTS_AUTHOR = "Author"
COMMENTS_BODY = "body"
COMMENTS_CREATED = "timestamp"
COMMENTS_ID = "Id"
COMMENTS_LINKID = "Link Id"
COMMENTS_PARENTID = "Parent Id"
COMMENTS_SCORE = "num_upvotes"

Subreddit = "python"
#The number of columns of data storeed for submissions and submission posts
SUBMISSIONCOLUMNS = 11
COMMENTCOLLUMNS = 7

##Analyzed data Static Variables
IF_COUNT = "If_Count"
THEN_COUNT = 'Then_Count'
NUM_COUNT = 'Num_Count'
ETHOS_COUNT = 'Num_Ethos_Keys'
LOGOS_COUNT = 'Num_Logos_Keys'
ANGER_SCORE = 'Anger_Score'
FEAR_SCORE = 'Fear_Score'
HAPPY_SCORE = 'Happy_Score'
SAD_SCORE = 'Sad_Score'
SURPRISE_SCORE = 'Surprise_Score'
LOGOS_CLASSIFICATION_PERCENT = 'Logos_Class'
ETHOS_CLASSIFICATION_PERCENT = 'Ethos_Class'
PATHOS_CLASSIFICATION_PERCENT = 'Pathos_Class'



def getSubmissionMetaData(posts, submissionIndex, submission):
    """ Function that collects metadata for a submission and stores it in an np array
    :param posts: np array that stores collection of metadata
    :param submissionIndex: location in np array metadata is stored
    :param submission: submission object
    :return: returns row of data pertaining to submission
    """
    posts[submissionIndex, 0] = submission.title
    posts[submissionIndex, 1] = submission.author
    posts[submissionIndex, 2] = submission.created_utc
    posts[submissionIndex, 3] = submission.distinguished
    posts[submissionIndex, 4] = submission.edited
    posts[submissionIndex, 5] = submission.id
    posts[submissionIndex, 6] = submission.locked
    posts[submissionIndex, 7] = submission.name
    posts[submissionIndex, 8] = submission.num_comments
    posts[submissionIndex, 9] = submission.score
    posts[submissionIndex, 10] = submission.upvote_ratio

    return posts

def getCommentMetaData(comments, commentIndex, comment):
    """ Function that collects metadata for a submission comment and stores it in an np array
    :param comments: np array that stores collection of metadata
    :param commentIndex: location in np array metadata is stored
    :param comment: submission comment object
    :return: returns row of data pertaining to submission comment
    """
    comments[commentIndex, 0] = comment.author
    comments[commentIndex, 1] = comment.body
    comments[commentIndex, 2] = comment.created_utc
    comments[commentIndex, 3] = comment.id
    comments[commentIndex, 4] = comment.link_id
    comments[commentIndex, 5] = comment.parent_id
    comments[commentIndex, 6] = comment.score
    return comments



def scrapeToCsv(pullSize, subreddit):
    """ Function that scrapes data from Reddit
    :param pullSize: (int) number of submissions to collect from a subreddit
    :param subreddit: (string) string name of Reddit Subreddit
    :return: returns pandas dataframe object of collected data
    """
    reddit = praw.Reddit(client_id='3MtQ8leeP8FYgNP0Vp6LJw', #Derived from reddit account
                         client_secret='gZudwyXvNcPua09iVG8q42Xgmsgvqg', #Derived from reddit account
                         username='PrawTutorialGT', #Reddit Username
                         password='jn_RMQSsX-7kAMn', #Reddit Username Password
                         user_agent='meow') #Needs to be filled but is not used

    subreddit = reddit.subreddit(subreddit)
    hotPython = subreddit.hot(limit=pullSize)
        #U200 for 200 unichars for whole title
    posts = np.empty((pullSize, SUBMISSIONCOLUMNS), dtype=np.dtype('U2000'))
    submissionIndex = 0
    isFirst = True
    for submission in hotPython:
        submission.comments.replace_more(limit=None)
        posts = getSubmissionMetaData(posts, submissionIndex, submission)
        comment_queue = submission.comments[:]
        numComments = submission.num_comments
        comments = np.empty((numComments + 10000, COMMENTCOLLUMNS), dtype=np.dtype('U2000'))
        commentIndex = 0
        while comment_queue:
            comment = comment_queue.pop(0)
            comments = getCommentMetaData(comments, commentIndex, comment)
            commentIndex+=1
            comment_queue.extend(comment.replies)
        if not isFirst:
            allCommentsArray = np.concatenate((allCommentsArray, comments), axis=0)
        else:
            allCommentsArray = comments
            isFirst = False
        submissionIndex+=1


    postsDf = pd.DataFrame(allCommentsArray)
    postsDf = updateComments(postsDf)

    submissionDf = pd.DataFrame(posts)
    submissionDf = updateSubmissionCSV(submissionDf)
    return postsDf, submissionDf

def getIsRhetoric(post):
    """ Function that populates a dataframe cell with its classification of is rhetoric. Returns -1 because the cells simply need to be populated here
    :param post: submission comment object
    :return: -1 to indicate comment has not been analyzed for rhetoric
    """
    return -1

def updateSubmissionCSV(dF):
    dF.columns = [SUB_TITLE, SUB_AUTHOR, SUB_CREATED, SUB_DISTINGUISHED, SUB_EDITED, SUB_ID, SUB_LOCKED, SUB_NAME,
                       SUB_NUMCOM, SUB_SCORE, SUB_UPVOTE_RATIO]
    # dF = dF.assign(Upvotes=lambda x: x[SUB_SCORE] * x[SUB_UPVOTE_RATIO] / (2 * x[SUB_UPVOTE_RATIO] - 1),
    #                          Downvotes=lambda x: x["Upvotes"] - x[SUB_SCORE],
    #                IsRhetoric=lambda x:getIsRhetoric(x))
    dF[SUB_CREATED] = dF[SUB_CREATED].apply(lambda x: datetime.utcfromtimestamp(float(x)))
    return dF
def updateComments(dF):
    """ Function that formats column titles of a dataframe and formates centain data
    :param dF: (dataFrame) dataframe object containing scraped data
    :return:(dataFrame) returns modified dataFrame
    """
    dF.columns = [COMMENTS_AUTHOR, COMMENTS_BODY, COMMENTS_CREATED, COMMENTS_ID, COMMENTS_LINKID, COMMENTS_PARENTID, COMMENTS_SCORE]
    #Comments that were deleted are stored as empty cells, these must be converted to NAN types to be discarded from dataframe object
    dF.replace('', np.nan, inplace=True)
    dF = dF.dropna()
    #Timestamps are converted to human readable format
    dF[COMMENTS_CREATED] = dF[COMMENTS_CREATED].apply(lambda x: datetime.utcfromtimestamp(float(x)))
    #Posts are marked as not anayized for rhetoric
    dF = dF.assign(containsPersuasion=lambda x:getIsRhetoric(x))
    return dF


def scrape_post(url):
    """ Function collects comments from a submission url
    :param url: (string) url to post
    :return: (dataFrame) returns dataframe containing comments within a submission
    """
    reddit = praw.Reddit(client_id='3MtQ8leeP8FYgNP0Vp6LJw',
                         client_secret='gZudwyXvNcPua09iVG8q42Xgmsgvqg',
                         username='PrawTutorialGT',
                         password='jn_RMQSsX-7kAMn',
                         user_agent='meow')
    isFirst = True
    submissionIndex = 0
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=None)
    comment_queue = submission.comments[:]
    numComments = submission.num_comments
    comments = np.empty((numComments + 10000, COMMENTCOLLUMNS), dtype=np.dtype("U2000"))

    posts = np.empty((1, SUBMISSIONCOLUMNS), dtype=np.dtype(('U2000')))
    posts = getSubmissionMetaData(posts, 0, submission)
    commentIndex = 0
    while comment_queue:
        comment = comment_queue.pop(0)
        comments = getCommentMetaData(comments, commentIndex, comment)
        commentIndex +=1
        comment_queue.extend(comment.replies)
    if not isFirst:
        allCommentsArray = np.concatenate((allCommentsArray, comments), axis=0)
    else:
        allCommentsArray=comments
        isFirst = False
    submissionIndex+=1
    postsDf = pd.DataFrame(allCommentsArray)
    postsDf = updateComments(postsDf)

    submissionDf = pd.DataFrame(posts)
    submissionDf = updateSubmissionCSV(submissionDf)
    return postsDf, submissionDf


def scrape_sub(url):
    pull_size = 3
    return scrapeToCsv(pull_size, url)

def analyzePersuasiveness(data):
    """ Function that creates quantitative data used to classify a post flagged as rhetoric
    :param data: (dataFrame) dataFrame of data that has been marked as containing persuasion
    :return: (dataFrame) returns dataframe with added columns containing class specific data
    """

    """Used for Logos detection, itterates through data and counts number of 'if/then's and use of numbers"""
    data[IF_COUNT] = data[COMMENTS_BODY].apply(lambda x: x.lower().count("if"))
    data[THEN_COUNT] = data[COMMENTS_BODY].apply(lambda x: x.lower().count('then'))
    data[NUM_COUNT] = data[COMMENTS_BODY].apply(lambda x: sum(c.isdigit() for c in x))
    #Used for Ethos detection, itterates through data and counts number of proper nouns used
    data[ETHOS_COUNT] = data[COMMENTS_BODY].apply(
        lambda x: len([word for word, pos, in pos_tag(x.split()) if pos == 'NNP' or pos == 'NNPS']))

    """Used for pathos detection, itterates through data and runs sentiment analysis on each post
    classifies each post with 5 categories (Anger, Fear, Happy, Sad, Surprise) and gives each category
    from 0-1 with the total of all categories summing to 1"""
    anger, fear, happy, sad, surprise = [], [], [], [], []
    count = 0
    for _, row in data.iterrows():
        if count % 100 == 0:
            print(count)
        count += 1
        emotions = te.get_emotion(row[COMMENTS_BODY])
        anger.append(emotions.get("Angry"))
        fear.append(emotions.get("Fear"))
        happy.append(emotions.get("Happy"))
        sad.append(emotions.get("Sad"))
        surprise.append(emotions.get("Surprise"))
    data[ANGER_SCORE] = anger
    data[FEAR_SCORE] = fear
    data[HAPPY_SCORE] = happy
    data[SAD_SCORE] = sad
    data[SURPRISE_SCORE] = surprise
    data[LOGOS_COUNT] = data[IF_COUNT] + data[THEN_COUNT] + data[NUM_COUNT]
    return data

def classifyPersuasions(data):
    """ Function gives percentage categorization of a post as it relates to logos, ethos pathos
    :param data: (dataFrame) dataframe containing exclusivly posts marked as containing persuasion
    :return: (dataFrame) returns dataframe with added columns showing percentage relationship to rhetoric
    """

    """Itterates through data and normalizes metrics used for classification to give percentage of rhetoric type
    """
    for index, row in data.iterrows():

        sents = sent_tokenize(row[COMMENTS_BODY])
        numSent = len(sents)
        total = (row[LOGOS_COUNT] / numSent) + (row[ETHOS_COUNT] / numSent) + (
                    row[ANGER_SCORE] + row[FEAR_SCORE])
        if total != 0:
            data.loc[index, LOGOS_CLASSIFICATION_PERCENT] = (row[LOGOS_COUNT] / numSent) / total * 100
            data.loc[index, ETHOS_CLASSIFICATION_PERCENT] = row[ETHOS_COUNT] / numSent / total * 100
            data.loc[index, PATHOS_CLASSIFICATION_PERCENT] = row[ANGER_SCORE] + row[FEAR_SCORE] / total * 100
        else:
            data.loc[index, LOGOS_CLASSIFICATION_PERCENT] = 0
            data.loc[index, ETHOS_CLASSIFICATION_PERCENT] = 0
            data.loc[index, PATHOS_CLASSIFICATION_PERCENT] = 0
    return data
