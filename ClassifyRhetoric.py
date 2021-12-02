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

import nltk
nltk.download('averaged_perceptron_tagger')


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
