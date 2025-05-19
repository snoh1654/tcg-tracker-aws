def sanitize_value(value):
    """
    Sanitizes value to prevent issues in URLs and API requests.
        - Replaces '/' with '-'
    """
    return value.replace("/", "-")

def generate_pk(item):
    """
    Generates the partition key for a tcg item.
    """
    return f"SET#{item['set_name']}"

def generate_latest_sk(item):
    """
    Generates SK for LATEST row item.
    """
    return f"CARD_LATEST#{item['card_id']}"

def generate_historical_sk(item):
    """
    Generates SK for HIST row item.
    """
    return f"CARD_HIST#{item['card_id']}#{item['timestamp']}"

def filter_static_data(item):
    """
    Add PK and SK and filter out static data from item.
    """
    allowed_keys = ["pk", "sk", "price", "currency", "source", "timestamp"]
    return {k: v for k, v in item.items() if k in allowed_keys}