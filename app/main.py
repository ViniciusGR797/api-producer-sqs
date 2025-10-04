import os
from fastapi import FastAPI
from mangum import Mangum
from routes import users, transactions

app = FastAPI(title="SQS API Lambda")

app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])

handler = Mangum(app)

if os.getenv("ENV") == "LOCAL":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)