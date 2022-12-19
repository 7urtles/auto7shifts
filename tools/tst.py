import requests

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
}

response = requests.get('http://blob:https://app.7shifts.com/ddc53ca3-f442-4b09-a335-548ef8570a59', headers=headers)