from fastapi import FastAPI
from routes import client, login

app = FastAPI(title="NDR Status Monitor")

# Include your routes
app.include_router(client.router)
app.include_router(login.router)

@app.get("/")
def root():
    return {"status": "NDR API is online"}