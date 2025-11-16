"""Vercel serverless entry point for the FastAPI backend."""

from mangum import Mangum

# Import the FastAPI instance defined in server.py
from server import app as fastapi_app  # noqa: E402

# Create an AWS Lambda-compatible handler that Vercel can invoke
handler = Mangum(fastapi_app, lifespan="off")
