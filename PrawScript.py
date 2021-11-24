import csv
from datetime import datetime

import numpy as np
import pandas as pd
import praw

#import CSVAnalyzer

##Submission Statics
SUBMISSION_CSV = "submissions.csv"
SUB_TITLE = "Title"
SUB_AUTHOR = "Author"
SUB_CREATED = "Created"
SUB_DISTINGUISHED = "Distinguished"
SUB_EDITED = "Edited"
SUB_ID = "Id"
SUB_LOCKED = "Locked"
SUB_NAME = "Name"
SUB_NUMCOM = "Num Comments"
SUB_SCORE = "Score"
SUB_UPVOTE_RATIO = "Upvote Ratio"

##Comment Statics
COMMENTS_CSV = "comments.csv"
COMMENTS_AUTHOR = "Author"
COMMENTS_BODY = "body"
COMMENTS_CREATED = "timestamp"
COMMENTS_ID = "Id"
#COMMENTS_ISSUBMITTER = "IsSubmitter"
COMMENTS_LINKID = "Link Id"
COMMENTS_PARENTID = "Parent Id"
COMMENTS_SCORE = "num_upvotes"

Subreddit = "python"
SUBMISSIONCOLUMNS = 11
COMMENTCOLLUMNS = 7
def getSubmissionMetaData(posts, submissionIndex, submission):
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
	comments[commentIndex, 0] = comment.author
	comments[commentIndex, 1] = comment.body
	comments[commentIndex, 2] = comment.created_utc
	comments[commentIndex, 3] = comment.id
	comments[commentIndex, 4] = comment.is_submitter
	comments[commentIndex, 5] = comment.link_id
	comments[commentIndex, 6] = comment.parent_id
	comments[commentIndex, 7] = comment.score
	return comments



def scrapeToCsv(pullSize, subreddit):
	reddit = praw.Reddit(client_id='3MtQ8leeP8FYgNP0Vp6LJw',
						 client_secret='gZudwyXvNcPua09iVG8q42Xgmsgvqg',
						 username='PrawTutorialGT',
						 password='jn_RMQSsX-7kAMn',
						 user_agent='meow')

	subreddit = reddit.subreddit(subreddit)
	hotPython = subreddit.hot(limit=pullSize)
		#U200 for 200 unichars for whole title
	posts = np.empty((pullSize, SUBMISSIONCOLUMNS), dtype=np.dtype('U200'))
	submissionIndex = 0
	isFirst = True
	for submission in hotPython:
		submission.comments.replace_more(limit=None)
		posts = getSubmissionMetaData(posts, submissionIndex, submission)
		comment_queue = submission.comments[:]
		numComments = submission.num_comments
		comments = np.empty((numComments, COMMENTCOLLUMNS), dtype=np.dtype('U200'))
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
	return postsDf
#pd.DataFrame(posts).to_csv(SUBMISSION_CSV, index = False)
	updateSubmissionCSV(SUBMISSION_CSV)

	pd.DataFrame(allCommentsArray).to_csv(COMMENTS_CSV, index = False)
	deletedNum = updateCommentsCSV(COMMENTS_CSV)
	print("Deleted comment Num: " + str(deletedNum))

def collectTrainData():
	reddit = praw.Reddit(client_id='3MtQ8leeP8FYgNP0Vp6LJw',
						 client_secret='gZudwyXvNcPua09iVG8q42Xgmsgvqg',
						 username='PrawTutorialGT',
						 password='jn_RMQSsX-7kAMn',
						 user_agent='meow')

	# getting sub
	subreddit = reddit.subreddit('pics')  # used changemyview and pics for data
	# getting top posts
	top_posts = subreddit.top("all", limit=500)
	# rows of csv
	comment_bodies = []

	# colls of csv
	details = ['body', 'containsPersuasion']

	# for keeping track of current post
	count = 1

	# for writing to the csv file
	with open('persuasionExamples.csv', 'a') as f:
		write = csv.writer(f)
		try:
			write.writerow(details)
		except:
			print("woop woop")  # used to catch an error (i think caused by untypable characters (emojis))
		for post in top_posts:
			post.comments.replace_more(limit=0)  # gets rid of the MoreComments structure
			print("Working on post: ")  # for logs
			print(count)
			for comment in post.comments:
				curr_body = comment.body
				arr = [curr_body]
				arr.append([0])  # use 0 or 1 for containsPursuasion or not (1 for changemyview, 0 for pics)
				try:
					write.writerow(arr)  # appends comment to csv file
				except:
					print("woop woop")  # same as other one

			# comment_bodies.append(arr)
			count += 1

	print("Done!")

def getIsRhetoric(post):
	return -1

def updateSubmissionCSV(file):
	dF = pd.read_csv(file, sep=",")
	dF.columns = [SUB_TITLE, SUB_AUTHOR, SUB_CREATED, SUB_DISTINGUISHED, SUB_EDITED, SUB_ID, SUB_LOCKED, SUB_NAME,
					   SUB_NUMCOM, SUB_SCORE, SUB_UPVOTE_RATIO]
	dF = dF.assign(Upvotes=lambda x: x[SUB_SCORE] * x[SUB_UPVOTE_RATIO] / (2 * x[SUB_UPVOTE_RATIO] - 1),
							 Downvotes=lambda x: x["Upvotes"] - x[SUB_SCORE],
				   IsRhetoric=lambda x:getIsRhetoric(x))
	dF[SUB_CREATED] = dF[SUB_CREATED].apply(lambda x: datetime.utcfromtimestamp(x))
	dF.to_csv(file, index=False)

def updateComments(dF):
	#deleted = 0
	#dF = pd.read_csv(file, sep=",")
	dF.columns = [COMMENTS_AUTHOR, COMMENTS_BODY, COMMENTS_CREATED, COMMENTS_ID, COMMENTS_ISSUBMITTER, COMMENTS_LINKID, COMMENTS_PARENTID, COMMENTS_SCORE]
	dF.replace('', np.nan, inplace=True)#deleted = dF.isna().sum()
    
	dF = dF.dropna()
	dF[COMMENTS_CREATED] = dF[COMMENTS_CREATED].apply(lambda x: datetime.utcfromtimestamp(float(x)))
	dF = dF.assign(containsPersuasion=lambda x:getIsRhetoric(x))
	#dF.to_csv(file, index=False)
	return dF

def readCsv(file):
	dataFrame = pd.read_csv(file, sep=",")
	return dataFrame

def scrape_post(url):
	reddit = praw.Reddit(client_id='3MtQ8leeP8FYgNP0Vp6LJw',
						 client_secret='gZudwyXvNcPua09iVG8q42Xgmsgvqg',
						 username='PrawTutorialGT',
						 password='jn_RMQSsX-7kAMn',
						 user_agent='meow')
	isFirst = True
	submissionIndex = 0
	submission = reddit.submission(url=url)
	comment_queue = submission.comments[:]
	numComments = submission.num_comments
	comments = np.empty((numComments, COMMENTCOLLUMNS), dtype=np.dtype("U200"))
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
	return postsDf


def scrape_sub(url):
	pull_size = 3
	scrapeToCsv(pull_size, url)

def main():
	#scrapeToCsv(3)
	#woof = CSVAnalyzer.CSVAnalyzer()
	#subDF = readCsv(SUBMISSION_CSV)

	p
	#comDF = readCsv(COMMENTS_CSV)

	#woof.plot(comDF, "Created", "Score")
	#woof.getParseTree(comDF["Body"][0])
	# negs = comDF.loc[comDF["Score"] < 0]
	# authNum = comDF["Author"].value_counts()
	# # print(negs)
	# # print(authNum)

	#print(woof.getWordUsage("YouTube", comDF, False))




if __name__ == '__main__':
	main()
