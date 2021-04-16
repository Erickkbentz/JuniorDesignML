import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import datetime
import sys
import pylab
import re
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D
matplotlib.axes.Axes.pie
matplotlib.pyplot.pie


def getKeys(dict):
	return dict.keys()


def getVals(dict):
	return dict.values()

def getCommentCount(arr):
	count = 0
	for i in arr:
		if i == "Comment":
			count +=1

	return count



def getCharts():
	return

	# Score vs Comments Chart
def scoreToCommentsChart(scoreToComments):
	scoreToComments = np.sort(scoreToComments, axis=1)
	fig, ax = plt.subplots()
	ax.set_yscale('log')
	ax.set_xlabel("Number of comments")
	ax.set_ylabel("Score")
	ax.set_ylim([0.1, 1500])
	plt.gca().scatter(scoreToComments[1], scoreToComments[0])
	plt.title("Score to Comments")
	matplotlib.pyplot.show()

def getScoreToCommentsStats(score, comments):
	print("Median Score: " + str(np.median(score)))
	print("Median number of Comments " + str(np.median(comments)))
	print("Average Score: " + str(np.average(score)))
	print("Average number of Comments " + str(np.average(comments)))
	print("STD Score : " + str(np.std(score)))
	print("STD number of Comments: " + str(np.std(comments)))

def postsToTimeChart(timestamp):
	# Posts vs Time chart
	fig, ax = plt.subplots()
	timestamp = [datetime.datetime.strptime(d[:10], "%Y-%m-%d").date() for d in timestamp[1:]]
	timeStamp = np.array(timestamp)
	timecount = np.zeros(timeStamp.shape)
	ax.set_ylabel("Number of Posts")
	ax.set_xlabel("Date")
	count = 0
	for i in timeStamp:
		timecount[count] = np.count_nonzero(timeStamp == i)
		count += 1

	plt.gca().scatter(timeStamp, timecount)
	plt.title("Number of Posts over time")
	matplotlib.pyplot.show()


# Posts vs Comments
def postsToCommentsChart(titles):
	print("Comments: " + str(getCommentCount(titles[1:])))
	print("total: " + str(len(titles[1:])))
	fig, ax = plt.subplots()
	numCommets = getCommentCount(titles[1:])
	labels = 'Comments: ' + str(numCommets), 'Posts: ' + str(len(titles[1:]) - numCommets)
	ax.pie([numCommets, len(titles[1:]) - numCommets], explode=(0, 0), labels=labels, autopct='%1.1f%%')
	ax.axis('equal')
	plt.title("Types of Content")
	plt.show()

def rhetoricCountNonClassifiedChart(body, total, logosCt, ethosCt, pathosCt):
	# pie chart with nonclassified
	labels = 'Logos: ' + str(logosCt), 'Ethos: ' + str(ethosCt), 'Pathos: ' + str(pathosCt), 'Non-Classified: ' + str(
		len(body) - total)
	sizes = [(logosCt / len(body)), (ethosCt / len(body)), (pathosCt / len(body)), (len(body) - total) / len(body)]
	explode = (0, 0, 0, 0)
	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
			shadow=True, startangle=90)
	ax1.axis('equal')
	plt.savefig('mainpie.png', format='png')
	plt.title("Percent Rhetoric of all Posts")
	plt.show()

def rhetoricCountClassifiedChart(body, total, logosCt, ethosCt, pathosCt):
	# pie chart without nonclassified
	labels = 'Logos: ' + str(logosCt), 'Ethos: ' + str(ethosCt), 'Pathos: ' + str(pathosCt)
	sizes = [(logosCt / total), (ethosCt / total), (pathosCt / total)]
	explode = (0, 0, 0)
	fig1, ax1 = plt.subplots()
	ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
			shadow=True, startangle=90)
	ax1.axis('equal')
	plt.savefig('mainpie.png', format='png')
	plt.title("Percent Rhetoric of classified posts")
	plt.show()

def totalRhetoricUsageChart(logosCt, ethosCt, pathosCt):
	# Main bar chart
	data = [logosCt, ethosCt, pathosCt]
	plt.bar(["Logos", "Ethos", "Pathos"], data, color="blue")
	plt.xlabel("Type of Rhetoric")
	plt.ylabel("Number Times Detected")
	plt.title("Total Rhetoric Usage")
	plt.savefig('mainbar.png', format='png')
	plt.show()

def rhetoricIndivCountChart(rhetoric, lpe):
	# logos bar chart
	logosKeys = getKeys(rhetoric)
	logosVals = getVals(rhetoric)
	plt.bar(logosKeys, logosVals, color="blue")
	plt.savefig(lpe +'bar.png', format='png')
	plt.title(lpe + " Words Counts")
	plt.ylabel("Frequency")
	plt.xlabel("Words scanned for")
	plt.show()

def getCharts(scoreToComments, timestamp, titles, body, logosCt, pathosCt, ethosCt, logos, ethos, pathos):
	scoreToCommentsChart(scoreToComments)
	postsToTimeChart(timestamp)
	postsToCommentsChart(titles)

	total = (logosCt + pathosCt + ethosCt)
	rhetoricCountNonClassifiedChart(body, total, logosCt, pathosCt, ethosCt)
	rhetoricCountClassifiedChart(body, total, logosCt, pathosCt, ethosCt)
	totalRhetoricUsageChart(logosCt, ethosCt, pathosCt)
	rhetoricIndivCountChart(logos, "Logos")
	rhetoricIndivCountChart(ethos, "Ethos")
	rhetoricIndivCountChart(pathos, "Pathos")


def main():
	import csv
	logos = {"study": 0, "studies": 0, 'percent': 0, 'statistics': 0, 'experts': 0, 'cdc': 0,'I am':0, 'I got': 0, 'I\'ve been': 0, 'I have':0}
	ethos = {'experience': 0, 'dr.': 0, 'doctor': 0, 'confident': 0}
	pathos = {'pathos': 0, 'test': 0, 'friend': 0, 'sad': 0, 'want': 0}
	logosCt = 0
	ethosCt = 0
	pathosCt = 0
	# and so on
	with open('reddit_vm.csv', mode='r', errors='ignore') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		count = 0
		titles = list()
		score = list()
		ids = list()
		urls = list()
		comments = list()
		created = list()
		timestamp = list()
		body = list()
		# CSV Reader loop; takes csv file and puts data into lists
		for row in csv_reader:
			curr_body = row[6]  # used to filter to just bodies of messages, current format isnt adaptive to multiple
			# data sets unless we specify format. can be removed at time cost
			word_arr = curr_body.split(" ")

			titles.append(row[0])
			score.append(row[1])
			ids.append(row[2])
			urls.append(row[3])
			comments.append(row[4])
			created.append(row[5])
			body.append(row[6])
			timestamp.append(row[7])
			for key in logos.keys():
				logos[key] += len(re.findall(key, curr_body))
				losgosCt += len(re.findall(key, curr_body))
			for word in word_arr:
				# logic to look for stuff
				word = word.lower()
				if ethos.__contains__(word):
					ethos[word] += 1
					ethosCt += 1
				if pathos.__contains__(word):
					pathos[word] += 1
					pathosCt += 1
		
		# Score vs comment #s
		score = [int(i) for i in score[1:]]
		comments = [int(i) for i in comments[1:]]
		scoreToComments = np.array((score[1:], comments[1:]))
		getScoreToCommentsStats(score, comments)

		

		print(logos)
		print(ethos)
		print(pathos)
		getCharts(scoreToComments, timestamp, titles, body, logosCt, pathosCt, ethosCt, logos, ethos, pathos)



if __name__ == '__main__':
	main()

