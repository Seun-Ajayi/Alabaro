"""
serialize Image Data
"""

import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event["s3_key"] ## TODO: fill in
    bucket = event["s3_bucket"] ## TODO: fill in

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        "image_data": image_data,
        "s3_bucket": bucket,
        "s3_key": key,
        "inferences": []

    }


"""
Image Classifier

"""

import os
import io
import boto3
import json
import base64

# Set the environment variable
ENDPOINT_NAME = "image-classification-2023-10-20-20-46-51-552"

# Initialize the SageMaker runtime client
runtime = boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    # Decode the image data
    print(event.keys())
    
    image = base64.b64decode(event["image_data"])

    # Instantiate a Predictor
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                    ContentType='image/png',
                                    Body=image) ## TODO: fill in
    # For this model the IdentitySerializer needs to be "image/png"
    #predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction:
    inferences = json.loads(response['Body'].read().decode())

    # We return the data back to the Step Function
    event["inferences"] = inferences
    return {
        'statusCode': 200,
        "image_data": event["image_data"],
        "s3_bucket": event["s3_bucket"],
        "s3_key": event["s3_key"],
        "inferences": event["inferences"]
    }


"""
Inference Confidence Filter
"""

import json


THRESHOLD = .93

def lambda_handler(event, context):
    # Get the inferences from the event
    inferences = event["inferences"]
    
    # Check if any values in any inferences are above THRESHOLD
    meets_threshold = (max(inferences) > THRESHOLD)
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        "image_data": event["image_data"],
        "s3_bucket": event["s3_bucket"],
        "s3_key": event["s3_key"],
        "inferences": event["inferences"]
    
    }