#!/usr/bin/python3
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Import bot API token
    token = os.environ.get("api-token")
