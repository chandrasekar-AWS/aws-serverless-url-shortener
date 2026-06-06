import json
import boto3
import string
import random
import os
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'url-shortener-table')
BASE_URL = os.environ.get('BASE_URL', 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod')

table = dynamodb.Table(TABLE_NAME)


def generate_short_code(length=6):
    """Generate a random alphanumeric short code."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def create_short_url(long_url):
    """Create a new short URL and store it in DynamoDB."""
    short_code = generate_short_code()

    # Ensure uniqueness
    while True:
        response = table.get_item(Key={'short_code': short_code})
        if 'Item' not in response:
            break
        short_code = generate_short_code()

    # Store in DynamoDB
    table.put_item(
        Item={
            'short_code': short_code,
            'long_url': long_url,
            'created_at': datetime.utcnow().isoformat(),
            'click_count': 0
        }
    )

    short_url = f"{BASE_URL}/{short_code}"
    return short_url, short_code


def get_long_url(short_code):
    """Retrieve the original URL from DynamoDB and increment click count."""
    response = table.get_item(Key={'short_code': short_code})

    if 'Item' not in response:
        return None

    # Increment click count
    table.update_item(
        Key={'short_code': short_code},
        UpdateExpression='SET click_count = click_count + :val',
        ExpressionAttributeValues={':val': 1}
    )

    return response['Item']['long_url']


def lambda_handler(event, context):
    """Main Lambda handler — routes POST (shorten) and GET (redirect)."""

    http_method = event.get('httpMethod', '')
    path = event.get('path', '/')
    path_params = event.get('pathParameters') or {}

    # ── POST /shorten — create a short URL ──────────────────────────────────
    if http_method == 'POST' and path == '/shorten':
        try:
            body = json.loads(event.get('body', '{}'))
            long_url = body.get('url', '').strip()

            if not long_url:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Missing "url" in request body'})
                }

            if not long_url.startswith(('http://', 'https://')):
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'URL must start with http:// or https://'})
                }

            short_url, short_code = create_short_url(long_url)

            return {
                'statusCode': 201,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'short_url': short_url,
                    'short_code': short_code,
                    'original_url': long_url
                })
            }

        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }

    # ── GET /{short_code} — redirect to original URL ─────────────────────────
    elif http_method == 'GET' and path_params.get('short_code'):
        short_code = path_params['short_code']
        long_url = get_long_url(short_code)

        if not long_url:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Short URL not found'})
            }

        return {
            'statusCode': 301,
            'headers': {'Location': long_url},
            'body': ''
        }

    # ── Fallback ─────────────────────────────────────────────────────────────
    return {
        'statusCode': 400,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Invalid request'})
    }
