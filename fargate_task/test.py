import requests
import time

url = "https://g6dnz1u2ml.execute-api.eu-west-2.amazonaws.com/minecraft-prod/command"
headers = {"Content-Type": "application/json"}
data = {"command": "start"}

print("starts")
response = requests.post(url, headers=headers, json=data)
print(response.status_code, response.json())
# If you want the script to wait until a response is received before proceeding, 
# you can use a while loop to keep checking the status of the response.
while response.status_code != 200:  # If status code is not 200
    print(f"Got status code {response.status_code}, retrying in 5 seconds...")
    time.sleep(5)  # Wait for 5 seconds before trying again
    response = requests.post(url, headers=headers, json=data)

print(response.status_code, response.json())
