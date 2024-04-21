import boto3
import os
from botocore.exceptions import ClientError

REGION = os.getenv('AWS_DEFAULT_REGION')
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

sqs = boto3.client(
    'sqs',
    region_name=REGION,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

queue_url = "https://sqs.us-east-1.amazonaws.com/440848399208/ycq2zz" 

def delete_message(handle):
    try:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=handle
        )
        print("Message deleted")
    except ClientError as e:
        print(e.response['Error']['Message'])

def get_message():
    messages = []
    try:
        while len(messages) < 10:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=['All'],
                MaxNumberOfMessages=1, 
                WaitTimeSeconds=20,
                MessageAttributeNames=['All']
            )
            if "Messages" in response:
                messages.extend(response['Messages'])
            else:
                print("Waiting for more messages...")
                continue

        sorted_messages = sorted(
            [(int(msg['MessageAttributes']['order']['StringValue']), 
              msg['MessageAttributes']['word']['StringValue'], 
              msg['ReceiptHandle'])
             for msg in messages],
            key=lambda x: x[0]
        )

        phrase = ' '.join(word for _, word, _ in sorted_messages)
        print("Assembled phrase:", phrase)

        with open('phrase.txt', 'w') as file:
            file.write(phrase)

        for _, _, handle in sorted_messages:
            delete_message(handle)

    except ClientError as e:
        print("Failed to fetch messages:", e.response['Error']['Message'])

if __name__ == "__main__":
    get_message()
