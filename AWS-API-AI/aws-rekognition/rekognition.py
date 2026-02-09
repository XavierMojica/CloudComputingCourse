#*********************************************************************************************************************
# Author - Xavier M
# Demoing AWS Rekognition APIs
#*********************************************************************************************************************
#Set UP 
# Use SSH to the EC2 instance and do the following
# ssh -i PEM-FILE ubuntu@IP

# sudo apt install python3-pip -y
# sudo apt install zip -y
# sudo apt install awscli -y

# pip3 install boto3
# pip3 install --upgrade awscli

# aws configure

# sudo chmod 777 -R /opt
# cd /opt
# wget https://github.com/XavierMojica/CloudComputingCourse/tree/0e6bbf31ef376a943bf2aa4c73ddd44515c5ede6/AWS-API-AI/aws-rekognition
# unzip aws-rekognition.zip  #unzip if the file is zipped else not needed


import boto3
import json


def rekognize(client, imageFile):
    #We will read the file from the local disk instead from S3
    with open(imageFile, 'rb') as image:
        filecontents = image.read()
        rekognition_txt = client.detect_text(Image={'Bytes': filecontents})
        rekognition_labels = client.detect_labels(Image={'Bytes': filecontents})
        rekognition_faces = client.detect_faces(Image={'Bytes': filecontents})
        #response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})

    return (rekognition_txt, rekognition_labels, rekognition_faces)

#Code for rekognition to recognize Text data
def extractText(rekog_response):
    print("==============================================================================================================================")
    #print(json.dumps(rekog_response, indent=4, sort_keys=True))
    textDetections=rekog_response['TextDetections']
    print('Detected text')
    for text in textDetections:
        print(text['DetectedText'], end=" ")
    print("\n")

#Code to recognize Labels
def extractLabels(rekog_response):
    print ("=============================================================================================================================")
    #print(json.dumps(rekog_response, indent=4, sort_keys=True))
    print('Detected labels in ' + imageFile)
    for label in rekog_response['Labels']:
        print("Label name is", label['Name'], "with parents", label['Parents'], "having confidence", label['Confidence'])
    print("")

#Code to recognize Faces
def extractFaces(rekog_response):
    print("=============================================================================================================================")
    #print(json.dumps(rekog_response, indent=4, sort_keys=True))
    print('Details of faces in ' + imageFile)
    for faceDetail in rekog_response['FaceDetails']:
        print("Face found with", faceDetail['Confidence'],"% confidence", "Features found are", end=" ")
        for feature in faceDetail['Landmarks']:
            print(feature['Type'], end=" ")
        print("")


#File ingestion, file to be recognized 
if __name__ == "__main__":
    client=boto3.client('rekognition')
    #Captcha.jpg Observation.jpeg soup-spoon.jpeg DennisRitchieVSSteveJobs.jpeg cheap-vs-quality.jpeg Dilbert-officepolitics.jpeg
    imageFile = 'FileName.jpeg' #add the file name 
    rekognition_txt, rekognition_labels, rekognition_faces = rekognize(client, imageFile)
    extractText(rekognition_txt)
    extractLabels(rekognition_labels)
    extractFaces(rekognition_faces)
    print("\nAll done.")
