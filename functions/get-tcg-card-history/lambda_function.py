import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('tcg')

def lambda_handler(event, context):
    try:
        # Extract card_id and set_name from path parameters
        path_parameters = event.get("pathParameters", {})
        set_name = path_parameters.get("set_name")

        card_id = event.get("queryStringParameters", {}).get("card-id")
        start_date = int(event.get("queryStringParameters", {}).get("start_date", 14))

        if not card_id:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "card_id is required"})
            }
        card_id = unquote(card_id)
        if not set_name:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "set_name is required"})
            }
        set_name = unquote(set_name)
        
        # Create pk
        pk = f"SET#{set_name.replace('%20', ' ')}"

        # Create sk
        sk_prefix = f"CARD_HIST#{card_id.replace('%20', ' ')}#"
        start_range = sk_prefix + _get_iso_datetime(start_date)
        end_range = sk_prefix + datetime.now(timezone.utc).isoformat()

        # Query DynamoDB for the number of historical card data asked by query parameter, default is 30
        response = table.query(
            KeyConditionExpression=Key('pk').eq(pk) & Key('sk').between(start_range, end_range), 
            ScanIndexForward=False,
            ProjectionExpression='#ts, price, company',
            ExpressionAttributeNames={'#ts': 'timestamp'},
        )

        # 404 Error if no card with card_id is found
        if not response["Count"]:
            return {
                'statusCode': 404,
                'body': json.dumps({"error": f"No records found for the given card_id. {card_id}"})
            }

        # Return retrieved data
        return {
            'statusCode': 200,
            'body': json.dumps(response.get('Items', []))
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": f"{card_id}"})
        }

def _get_iso_datetime(days_away: int) -> str:
    """
    Gets isoformat of date that is days_away from current time
    """
    target_date = datetime.now(timezone.utc).date() - timedelta(days=days_away)
    midnight_datetime = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    return midnight_datetime.isoformat()
