import requests
from dotenv import load_dotenv
import os

load_dotenv()

GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

url = "https://gitlab.com/api/v4/user"

headers = {
    "PRIVATE-TOKEN": GITLAB_TOKEN
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())