import requests

url = "https://discord.com/api/v8/applications/697790419035226112/commands"

roll_json = {
    "name": "roll",
    "type": 1,
    "description": "Roll some dice",
    "options": [
        {
            "name": "dice",
            "description": "The dice to roll",
            "type": 3,
            "required": True,
        }
    ]
}

headers = {
    "Authorization": ""
}
    
r = requests.post(url, headers=headers, json=roll_json)

