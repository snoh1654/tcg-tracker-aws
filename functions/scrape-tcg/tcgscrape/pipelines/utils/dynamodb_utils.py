from .item_utils import generate_pk, generate_latest_sk
from .s3_utils import upload_img_to_s3
from botocore.exceptions import ClientError

def get_expression_values(item):
    """
    Create attribute values for DynamoDB.
    """
    return {f":{key}": val for key, val in item.items()}

def get_update_expression(item):
    """
    Create update expression for DynamoDB.
    """
    return "SET " + ", ".join([f"#{key} = :{key}" for key in item.keys()])

def update_latest(table, bucket, item):
    """
    Update the latest row in DynamoDB. If row with corresponding keys do not exist, create the row and upload img to s3.
    """

    pk = generate_pk(item)
    sk = generate_latest_sk(item)

    # pop image_src since we do not store the scraped website's img url
    image_src = item.pop("image_src")

    # Update row with corresponding IDs, throws an exception if corresponding row does not exist
    expression_values = get_expression_values(item)
    update_expression = get_update_expression(item)

    try:
        response = table.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression=update_expression,
            ExpressionAttributeNames={f"#{key}": key for key in item if key not in ["pk", "sk"]},
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW",
            ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)"
        )
    # First time adding card_id in set_name to DB
    except ClientError:
        # Download img within item["image_src"] and add it to s3 bucket
        # Update image_src to be the url ending of the s3 object. 
        item["image_src"] = upload_img_to_s3(bucket, item, image_src)
        item["initial_record_date"] = item["timestamp"]

        expression_values = get_expression_values(item)
        update_expression = get_update_expression(item)
        response = table.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression=update_expression,
            ExpressionAttributeNames={f"#{key}": key for key in item if key not in ["pk", "sk"]},
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print(e)

    return response

def batch_write(table, buffer):
    """
    Batch write items to DynamoDB.
    """
    with table.batch_writer() as batch:
        for item in buffer:
            batch.put_item(Item=item)
    return {"status": "success"}
