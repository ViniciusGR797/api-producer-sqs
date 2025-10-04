import os
from fastapi import FastAPI
from mangum import Mangum
from routes import users, messages

app = FastAPI(
    title="Practical Challenge - Mid-Level Platform Engineer",
    description="""
**Objective:** Develop a RESTful API for integration with AWS SQS,
allowing message production, status querying, and reprocessing
from a dead-letter queue (DLQ).

**Architecture:** The solution includes an API Gateway exposing endpoints,
a Lambda producer sending messages to SQS, a FIFO queue with DLQ,
and a Lambda consumer worker processing messages asynchronously.
Message metadata and idempotency are managed via DynamoDB.

**Authentication:** POST /users/login provides a token that must be
used in subsequent requests to authorize access to the other endpoints.

**CI/CD:** Lambdas are packaged as Docker images stored in AWS ECR,
with automated build and deployment pipelines.

**Observability:** Logs and metrics are sent to CloudWatch,
covering message counts, processing times, retries, and errors.

**Endpoints:**
- POST /messages/send: produce messages to SQS.
- GET /messages/status: query SQS and DLQ message counts.
- POST /messages/dlq/reprocess: reprocess DLQ messages to main queue.

**Design Considerations:**
- Asynchronous message consumption via Lambda worker.
- DLQ handling with prevention of loops and invalid messages.
- Idempotent processing using DynamoDB.
- Full OpenAPI/Swagger documentation.
- Containerized deployment with Docker.
- CI/CD integration with ECR.

This solution ensures a fully functional, observable, and
containerized message processing pipeline with AWS native services.
"""
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])

handler = Mangum(app)

if os.getenv("ENV") == "LOCAL":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
