#When triggered, this Lambda sends a notification and then shuts down a specific EC2 instance.
#This script is added to the Lambda > Functions > FnName > Code > Press DEPLOY
#MAKE SURE PERMISSIONS ARE SET IN IAM > ROLES > FN NAME> TO GIVE SNS FULL ACCESS AND EC2FULL ACCESS 

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

    return{
        'status': "Stop initiated", 
        'instance': INSTANCE_ID, 
        'sns_topic': SNS_TOPIC_ARN
    }
