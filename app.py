import json
import time
import os
from flask import Flask
from flask import request


analyze_job_fields = ['userId', 'jobId', 'jobName', 'inputType', 'url', 'fileLocation']

app = Flask(__name__)

@app.route('/analyze_job', methods=['POST'])
def analyze_job():
    reqData = request.json
    print('Request: ' + str(reqData))
    outputFileLocation = ''

    # add logic to change status if ML stuff fails or is run successfully, for now set to COMPLETED by defualt
    status = 'COMPLETED'
 
    # if ML stuff fails set outputLocation to empty string
    try:
        #------------------- FAKE DATA -----------------------
        elp = [86, 67, 91]
        persuasion = [81, 21]
        sentences = ["Sodium, atomic number 11, was first isolated by Humphry Davy in 1807.", "A chemical component of salt, he named it Na in honor of the saltiest region on earth, North America."]

        data = {
            'elp' : elp,
            'persuasion' : persuasion,
            'sentences' : sentences
        }

        # Relative path
        relativePathPrefix = "../"

        # File and Folder paths
        outputFolderLocation = "UserFiles/{}/outputFiles".format(str(reqData['userId']))
        fileName =  str(reqData['jobName']) + "-output.json"
        outputFileLocation = outputFolderLocation + "/"+ fileName

        

        #-------------- Check if output folder exists exists -----------------------
        if not (os.path.exists(relativePathPrefix + outputFolderLocation)):
            os.makedirs(relativePathPrefix + outputFolderLocation)


        with open(relativePathPrefix + outputFileLocation, "w") as outfile:
            json.dump(data, outfile)

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





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)