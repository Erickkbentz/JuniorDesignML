import praw
import numpy as np
import pandas as pd
import csv
import CSVAnalyzer
from datetime import datetime
from praw.models import MoreComments
from numpy import genfromtxt

SUBMISSIONCOLUMNS = 11
COMMENTCOLLUMNS = 8
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
COMMENTS_BODY = "Body"
COMMENTS_CREATED = "Created"
COMMENTS_ID = "Id"
COMMENTS_ISSUBMITTER = "IsSubmitter"
COMMENTS_LINKID = "Link Id"
COMMENTS_PARENTID = "Parent Id"
COMMENTS_SCORE = "Score"

Subreddit = "python"

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



def scrapeToCsv(pullSize):
	##PostData
	# author
	# comments:forrest
	# creationTime
	# fromModerator
	# isEdited
	# Id
	# locked
	# name
	# numcomments
	# score
	# title
	# upvoteratio

	##CommentData
	# author
	# body
	# creationTime
	# isauthor
	# id
	# parentid
	# score
	reddit = praw.Reddit(client_id='3MtQ8leeP8FYgNP0Vp6LJw',
						 client_secret='gZudwyXvNcPua09iVG8q42Xgmsgvqg',
						 username='PrawTutorialGT',
						 password='jn_RMQSsX-7kAMn',
						 user_agent='meow')

	subreddit = reddit.subreddit(Subreddit)
	hotPython = subreddit.hot(limit=pullSize)
		#U100 for 200 unichars for whole title
	posts = np.empty((pullSize, SUBMISSIONCOLUMNS), dtype=np.dtype('U200'))
	#allCommentsList = list()
	submissionIndex = 0
	isFirst = True
	deleted = 0
	for submission in hotPython:
		#print("Submission% " + str(submissionIndex/pullSize))
		submission.comments.replace_more(limit=None)

		posts = getSubmissionMetaData(posts, submissionIndex, submission)

		#print(posts.transpose(pullSize, 11).reshape(3, -1))
		comment_queue = submission.comments[:]
		numComments = submission.num_comments
		comments = np.empty((numComments, COMMENTCOLLUMNS), dtype=np.dtype('U200'))
		commentIndex = 0
		#commentsArray = np.empty((submission.num_comments, 8), dtype=np.dtype('U200'))
		while comment_queue:
			#print("Comment % " + str(commentIndex/submission.num_comments))
			comment = comment_queue.pop(0)
			# if comment.author == None:
			# 	deleted +=1
			# 	continue
			comments = getCommentMetaData(comments, commentIndex, comment)
			commentIndex+=1
			comment_queue.extend(comment.replies)

		#allCommentsList.append(comments)
		if not isFirst:
			allCommentsArray = np.concatenate((allCommentsArray, comments), axis=0)
		else:
			allCommentsArray = comments
			isFirst = False
		submissionIndex+=1

	#allComments = np.asarray(allCommentsList)
	#print(allCommentsArray)

	pd.DataFrame(posts).to_csv(SUBMISSION_CSV, index = False)
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

def updateCommentsCSV(file):
	deleted = 0
	dF = pd.read_csv(file, sep=",")
	dF.columns = [COMMENTS_AUTHOR, COMMENTS_BODY, COMMENTS_CREATED, COMMENTS_ID, COMMENTS_ISSUBMITTER, COMMENTS_LINKID, COMMENTS_PARENTID, COMMENTS_SCORE]
	deleted = dF.isna().sum()
	dF = dF.dropna()
	dF[COMMENTS_CREATED] = dF[COMMENTS_CREATED].apply(lambda x: datetime.utcfromtimestamp(x))
	dF = dF.assign(IsRhetoric=lambda x:getIsRhetoric(x))
	dF.to_csv(file, index=False)
	return deleted


def readCsv(file):
	dataFrame = pd.read_csv(file, sep=",")
	return dataFrame

def main():
	#scrapeToCsv(3)
	woof = CSVAnalyzer.CSVAnalyzer()
	subDF = readCsv(SUBMISSION_CSV)


	comDF = readCsv(COMMENTS_CSV)

	woof.plot(comDF, "Created", "Score")

	# negs = comDF.loc[comDF["Score"] < 0]
	# authNum = comDF["Author"].value_counts()
	# # print(negs)
	# # print(authNum)

	#print(woof.getWordUsage("YouTube", comDF, False))




if __name__ == '__main__':
	main()
