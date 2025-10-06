#!/bin/bash
set -e

export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

AWS="aws --endpoint-url=http://localhost:4566 --region $AWS_DEFAULT_REGION"

echo "Creating SQS queues..."
$AWS sqs create-queue --queue-name main_queue.fifo \
    --attributes FifoQueue=true,ContentBasedDeduplication=true || echo "Queue main_queue already exists"

$AWS sqs create-queue --queue-name dlq_queue.fifo \
    --attributes FifoQueue=true,ContentBasedDeduplication=true || echo "DLQ already exists"

LAMBDA_NAME="api-producer-sqs"
ZIP_FILE="infra/lambda_build/${LAMBDA_NAME}.zip"

if [ ! -f "$ZIP_FILE" ]; then
    echo "Error: Lambda zip not found ($ZIP_FILE). Run build-lambda.sh first."
    exit 1
fi

echo "Creating Lambda $LAMBDA_NAME..."
set +e
$AWS lambda create-function \
    --function-name $LAMBDA_NAME \
    --runtime python3.11 \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --handler main.handler \
    --zip-file fileb://$ZIP_FILE
if [ $? -ne 0 ]; then
    echo "Lambda $LAMBDA_NAME already exists"
fi
set -e

echo "Creating REST API Gateway..."
API_ID=$($AWS apigateway create-rest-api --name "fastapi_api" --query 'id' --output text)
ROOT_ID=$($AWS apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)

ROUTES=(
"/docs GET"
"/messages GET"
"/status/{queue_name} GET"
"/send POST"
"/dlq POST"
"/reprocess/{queue_name} POST"
"/openapi.json GET"
"/users/login POST"
)

for route in "${ROUTES[@]}"; do
    IFS=' ' read -r full_path method <<< "$route"

    parent_id=$ROOT_ID
    IFS='/' read -ra PARTS <<< "${full_path#/}"
    for part in "${PARTS[@]}"; do
        if [ -z "$part" ]; then
            continue
        fi
        res_id=$($AWS apigateway create-resource --rest-api-id $API_ID --parent-id $parent_id --path-part "$part" --query 'id' --output text 2>/dev/null || \
            $AWS apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/${full_path#/}'].id" --output text)
        parent_id=$res_id
    done

    $AWS apigateway put-method \
        --rest-api-id $API_ID \
        --resource-id $parent_id \
        --http-method $method \
        --authorization-type NONE

    $AWS apigateway put-integration \
        --rest-api-id $API_ID \
        --resource-id $parent_id \
        --http-method $method \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri arn:aws:apigateway:$AWS_DEFAULT_REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$AWS_DEFAULT_REGION:000000000000:function:$LAMBDA_NAME/invocations
done

echo "Deploying API..."
$AWS apigateway create-deployment --rest-api-id $API_ID --stage-name local

set +e
$AWS lambda add-permission \
    --function-name $LAMBDA_NAME \
    --statement-id apigateway-test-$RANDOM \
    --action "lambda:InvokeFunction" \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$AWS_DEFAULT_REGION:000000000000:$API_ID/*/*/*"
set -e

echo "=============================="
echo "LocalStack setup completed"
echo "REST API endpoint:"
echo "http://localhost:4566/restapis/$API_ID/local/_user_request_/"
echo "Queues: main_queue.fifo, dlq_queue.fifo"
echo "Lambda: $LAMBDA_NAME"
echo "=============================="
