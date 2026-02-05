#When triggered, this Lambda sends a notification and then shuts down a specific EC2 instance.
#This script is added to the Lambda > Functions > FnName > Code > Press DEPLOY
#MAKE SURE PERMISSIONS ARE SET IN IAM > ROLES > FN NAME> TO GIVE SNS FULL ACCESS AND EC2FULL ACCESS 
#Go to Lambda > functions > FnName> Configuration > Edit Environment variables, add INSTACE_ID into 1st Key then get the value from the ec2 
#then SNS_TOPIC_ARN into 2nd key and then get the value from  SNS > topics > fn name > ARN 


import boto3
import os 
from datetime import datetime

ec2 = boto3.client('ec2')
sns = boto3.client('sns')

INSTANCE_ID = os.environ['INSTANCE_ID']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    msg = f"Your instance {INSTANCE_ID} is being stopped now. Time: {datetime.now()}"
        #sending out the email 
    sns.publish(
        TopicArn = SNS_TOPIC_ARN,
        Subject = 'EC2 Stop Alert', 
        Message = msg
    )
    
    #stopping the instance
    ec2.stop_instances(InstanceIds=[INSTANCE_ID])

    #returns log that it was done
    return{
        'status': "Stop initiated", 
        'instance': INSTANCE_ID, 
        'sns_topic': SNS_TOPIC_ARN
    }
