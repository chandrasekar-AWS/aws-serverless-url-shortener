# Serverless URL Shortener using AWS Lambda, API Gateway and DynamoDB

## Overview
Built a fully serverless URL shortener — no servers to manage, fully
event-driven architecture using AWS managed services.

## Architecture
HTTP POST (Long URL) → API Gateway → Lambda (Python) → DynamoDB → Short URL returned

## What I Built
* Lambda function in Python to generate unique short codes
* API Gateway HTTP POST endpoint to accept long URLs
* DynamoDB table to store original URL and short code mapping
* Short link generation and return logic
* Fully serverless — zero infrastructure management

## Services Used
* AWS Lambda (Python)
* Amazon API Gateway
* Amazon DynamoDB
* Python
* AWS Management Console

## Key Learnings
* Serverless architecture design
* Event-driven computing with Lambda
* NoSQL data storage with DynamoDB
* REST API creation with API Gateway
* Cost-efficient cloud architecture (pay-per-use)
