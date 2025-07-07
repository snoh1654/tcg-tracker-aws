import json
import boto3
from boto3.dynamodb.conditions import Key
from urllib.parse import unquote

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('tcg')

def lambda_handler(event, context):
    try:
        # Extract tcg_Name properly from API Gateway event
        tcg_name = event.get("pathParameters", {}).get("tcg_name")
        if not tcg_name:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "set_name is required"})
            }
        tcg_name = unquote(tcg_name)

        # Replace %20 with spaces and generate corresponding PK in tcg table 
        pk = "TCG#" + tcg_name.replace("%20", " ")

        # Query DynamoDB for all sets belonging to tcg_name  
        response = table.query(
            KeyConditionExpression=Key('pk').eq(pk), 
            ScanIndexForward=False,
            ProjectionExpression='set_name', # !!! update to get proper image using s3 later
        )

        # 404 Error if no tcg with tcg_name is found
        if not response["Count"]:
            return {
                'statusCode': 404,
                'body': json.dumps({"error": "No records found for the given tcg_name "})
            }
        
        # Return retrieved data
        return {
            'statusCode': 200,
            'body': json.dumps(response.get('Items', []))  # Send actual query results
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
