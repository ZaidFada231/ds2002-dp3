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
    processed_messages = []
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

        for msg in messages:
            order = msg['MessageAttributes']['order']['StringValue']
            word = msg['MessageAttributes']['word']['StringValue']
            processed_messages.append({'order': int(order), 'word': word})

        print(processed_messages)
        sorted_messages = sorted(processed_messages, key=lambda x: x['order'])
        phrase = ' '.join(item['word'] for item in sorted_messages)
        print("Assembled phrase:", phrase)

        with open('phrase.txt', 'w') as file:
            file.write(phrase)

        for _, _, handle in sorted_messages:
            delete_message(handle)

    except ClientError as e:
        print("Failed to fetch messages:", e.response['Error']['Message'])

if __name__ == "__main__":
    get_message()
