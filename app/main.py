import os
from fastapi import FastAPI
from mangum import Mangum
from routes import users, messages

app = FastAPI(
    title="SQS API Lambda",
    root_path="",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])

handler = Mangum(app)

if os.getenv("ENV") == "LOCAL":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
