# pinterest_batch_poster/pinterest_api.py

import requests

PINTEREST_BASE_URL = "https://api.pinterest.com/v5"

def get_boards(api_key: str):
    url = f"{PINTEREST_BASE_URL}/boards"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        boards = response.json().get("items", [])
        return [board["name"] for board in boards]
    except requests.exceptions.RequestException as e:
        print(f"[Pinterest API] Error fetching boards: {e}")
        return []
