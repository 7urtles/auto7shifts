import requests

url = "https://api.7shifts.com/v2/companies"

headers = {
    "accept": "application/json",
    "authorization": "Bearer 37646466363966302d303737352d343238312d623239352d303862613537363639346563"
}

response = requests.get(url, headers=headers)

print(response.text)