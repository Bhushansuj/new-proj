from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import clients, login
import os

app = FastAPI()

app.include_router(clients.router)
app.include_router(login.router)

frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)