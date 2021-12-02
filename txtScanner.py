import pandas as pd
import re
from nltk import tokenize

def txtMain(filePath):
    text = open(filePath, 'r')
    text = text.read()
    data = pd.DataFrame(columns=['body'])
    breakup = text.splitlines()
    for cur in breakup:
        if (len(cur) > 5):
            data = data.append({'body':cur}, ignore_index=True)
    
    return data
