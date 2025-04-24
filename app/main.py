import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return responses.RedirectResponse(url="/docs", status_code=302)


app.include_router(routes.router, prefix="/api")