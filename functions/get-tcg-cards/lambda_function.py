import json
import boto3
from boto3.dynamodb.conditions import Key
from urllib.parse import unquote

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('tcg')

def lambda_handler(event, context):
    try:
        # Extract set_name properly from API Gateway event
        set_name = event.get("pathParameters", {}).get("set_name")
        if not set_name:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "set_name is required"})
            }
        set_name = unquote(set_name)

        # Replace %20 with spaces and generate corresponding PK in tcg table 
        pk = "SET#" + set_name.replace("%20", " ")

        # Query DynamoDB for all latest cards' information belonging to set_name 
        response = table.query(
            KeyConditionExpression=Key('pk').eq(pk) & Key('sk').begins_with('CARD_LATEST#'), 
            ScanIndexForward=False,
            ProjectionExpression='card_id, #n, price, initial_record_date',
            ExpressionAttributeNames={'#n': 'name'},
        )

        # 404 Error if no set with set_name is found
        if not response["Count"]:
            return {
                'statusCode': 404,
                'body': json.dumps({"error": f"No records found for the given set_name {set_name}"})
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
