import matplotlib.pyplot as plt
import spacy
from nltk.tokenize import sent_tokenize
from nltk import Tree

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
	#
	# def getNumPostsPerSub(self, subDf, comDf, column):
	# 	for row in subDf.itterrows():
	# 		comDf["Link Id"]


	def plot(self, df, xAxis, yAxis):
		df.plot(x=xAxis, y = yAxis)
		plt.show()

	def toTree(self, node):
		if node.n_lefts + node.n_rights > 0:
			return Tree(node.orth_,[self.toTree(child) for child in node.children])
		else:
			return node.orth_

	def getParseTree(self, text):
		nlp = spacy.load("en_core_web_sm")
		doc = nlp(text)
		[self.toTree(sent.root).pretty_print() for sent in doc.sents]