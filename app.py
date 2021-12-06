import json
import time
import os
from flask import Flask
from flask import request
import pandas as pd
import pickle
import csv
import numpy as np
from pdfScanner import pdfMain
from txtScanner import txtMain
from csvScanner import csvMain
from PrawScript import scrape_post, scrape_sub
from ClassifyRhetoric import analyzePersuasiveness, classifyPersuasions
import re
#import praw script file
#import filtering file
#import pdf scraper
#import text to df

analyze_job_fields = ['userId', 'jobId', 'jobName', 'inputType', 'url', 'fileLocation']

app = Flask(__name__)

@app.route('/analyze_job', methods=['POST'])
def analyze_job():
    reqData = request.json    
    
    #Detecting inputType, decided the data formatting route to take
    inputType = str(reqData['inputType'])
    inputFileLocation = ''
    data = pd.DataFrame()
    if (inputType == "URL"):
        #input is a url, first we check if its a sub or a post
        url = str(reqData['URL'])
        match = re.search('www\.reddit\.com\/r\/.*\/comments', url)
        try:
            if (match != None):
                #url is a post
                postData, submissionData = scrape_post(url)
            else:
                #url is a sub, first isolate the sub
                x = re.search("\.com\/r\/", url)
                sub = url[x.span()[1]:-1]
                postData, submissionData = scrape_sub(sub)
            data['body'] = postData['body']
            data['body'].append(submissionData['body'], ignore_index=True)
        except Exception as e:
            return ErrorResponse("PRAW Failed, Double check URL and try again. ERROR: " + str(e))
    else:
        inputFileLocation = str(reqData['fileLocation'])
        if (inputFileLocation[-3:] == 'pdf'):
            #Input is a pdf
            data = pdfMain(inputFileLocation)
        elif (inputFileLocation[-3:] == 'csv'):
            #Input is a csv
            data = csvMain(inputFileLocation)
        elif (inputFileLocation[-3:] == 'txt'):
            #Input is a txt
            data = txtMain(inputFileLocation)
        else:
            #Input file is invalid
            return ErrorResponse("Input file was not of right type! make sure the extension is" + 
                              " .pdf, .txt, or .csv")
            
    #Get the formatted data generated from above, run it through persuasionDetection model
    with open('model.pkl', 'rb') as f:
        persuasionDetection = pickle.load(f)
    with open('count_vec.pkl', 'rb') as f:
        count_vect = pickle.load(f)
   
    try: 
        input_x = data.body
        input_x_cv = count_vect.transform(input_x)    
        predictions = persuasionDetection.predict(input_x_cv)
        data['containsPersuasion'] = predictions
    except Exception as e:
        return ErrorResponse("Error running machine learning on data. ERROR: " + str(e))
    
    
    try:
        persuasiveData = data[data.containsPersuasion == 1] 
        numExamples = len(data.body)
        numPersuasiveExamples = len(persuasiveData.body)
    
        persuasiveData = analyzePersuasiveness(persuasiveData)
        persuasiveData = classifyPersuasions(persuasiveData)
        persuasiveData = persuasiveData.drop(columns=['If_Count',
                           'Then_Count',
                           'Num_Count',
                           'Num_Ethos_Keys',
                           'Anger_Score',
                           'Fear_Score',
                           'Happy_Score',
                           'Sad_Score',
                           'Surprise_Score',
                           'Num_Logos_Keys'])
              
        persuasiveData['id'] = persuasiveData.index + 1
        persuasiveData['numPersuasive'] = numPersuasiveExamples
        persuasiveData['numTotal'] = numExamples
    except Exception as e:
        return ErrorResponse("Error classifying rhetoric. ERROR: " + str(e))
    
    
    #persuasiveData.to_json('formatOutputs/testing.json', orient='records', lines=True)
    
    
    #persuasiveData.to_csv('formatOutputs/testingtesting.csv', index=False)
    
    #return "We did it :D", 100
    
    
    
    
    
    outputFileLocation = ''

    
    
    
    
    
    # add logic to change status if ML stuff fails or is run successfully, for now set to COMPLETED by defualt
    status = 'COMPLETED'
 
    # if ML stuff fails set outputLocation to empty string
    try:
        #------------------- FAKE DATA -----------------------
        # Relative path
        relativePathPrefix = "../"

        # File and Folder paths
        outputFolderLocation = "UserFiles/{}/outputFiles".format(str(reqData['userId']))
        fileName =  str(reqData['jobName']) + "-output.json"
        outputFileLocation = outputFolderLocation + "/"+ fileName

        

        #-------------- Check if output folder exists exists -----------------------
        if not (os.path.exists(relativePathPrefix + outputFolderLocation)):
            os.makedirs(relativePathPrefix + outputFolderLocation)


            
        #with open(relativePathPrefix + outputFileLocation, "w") as outfile:
         #   json.dump(, outfile)
            
        persuasiveData.to_json(relativePathPrefix + outputFileLocation, orient='records')


        if not (os.path.exists(relativePathPrefix + outputFileLocation)):
            status = 'FAILED'
            outputFileLocation = ''


        response = app.response_class(
            response=json.dumps({'status': status, 'outputLocation': outputFileLocation}),
            status=200,
            mimetype='application/json'
        )

        return response
    except Exception as e:
        response = app.response_class(
            response=json.dumps({"error" : e}),
            status=500,
            mimetype='application/json'
        )

    return response

def ErrorResponse(error):
    response = app.response_class(
            response=json.dumps({"error" : error}),
            status=500,
            mimetype='application/json')
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)