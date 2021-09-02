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
    "Authorization": "Bot Njk3NzkwNDE5MDM1MjI2MTEy.Xo8aKQ.Acg544rFljUP32eFs8Ugjw5U8bU"
}
    
r = requests.post(url, headers=headers, json=roll_json)

