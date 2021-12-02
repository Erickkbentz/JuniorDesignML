import pandas as pd
import csv

def csvMain(filePath):
    temp = pd.read_csv(filePath)
    data = pd.DataFrame(columns=['body'])
    data['body'] = temp['body']
            
    return data
