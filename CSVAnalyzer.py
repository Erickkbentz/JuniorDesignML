import matplotlib.pyplot as plt



class CSVAnalyzer():
	COMMENTBODY = "Body"
	COMMENTAUTHOR = "Author"
	COMMENTSCORE = "Score"
	COMMENTPARENTID = "Parent Id"



	def getWordUsage(self, word, dataFrame, isRegex):
		df = dataFrame[self.COMMENTBODY].str.contains(word, regex=isRegex)
		return df.value_counts()

	def getScoreSum(self, author, dataFrame):
		temp = dataFrame.loc[dataFrame[self.COMMENTAUTHOR] == author]
		return temp[self.COMMENTSCORE].sum()

	def getForrestSizes(self, dataFrame):
		return dataFrame[self.COMMENTPARENTID].value_counts()

	def getNumPostsPerSub(self, subDf, comDf, column):
		for row in subDf.itterrows():
			comDf["Link Id"]


	def plot(self, df, xAxis, yAxis):
		df.plot(x=xAxis, y = yAxis)
		plt.show()