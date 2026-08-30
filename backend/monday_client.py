import os
import requests
from pathlib import Path
from dotenv import load_dotenv


# Locate the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")


MONDAY_API_URL = "https://api.monday.com/v2"

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")


def monday_request(query, variables=None):

    if not MONDAY_API_TOKEN:
        raise ValueError(
            "MONDAY_API_TOKEN is missing. "
            "Check your .env file."
        )

    headers = {
        "Authorization": MONDAY_API_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(
        MONDAY_API_URL,
        headers=headers,
        json={
            "query": query,
            "variables": variables or {}
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise Exception(result["errors"])

    return result["data"]