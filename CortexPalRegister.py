import requests
import configparser
import time

url = "https://discord.com/api/v8/applications/697790419035226112/commands"

config = configparser.ConfigParser()
config.read('cortexpal.ini')

headers = {
    "Authorization": "Bot {}".format(config['discord']['token'])
}

print(headers)

info_json = {
    "name": "info",
    "type": 1,
    "description": "Show all game information for this channel."
}

print("Submitting info")
r = requests.post(url, headers=headers, json=info_json)
print(r.text)
time.sleep(5)

pin_json = {
    "name": "pin",
    "type": 1,
    "description": "Display game information in a pinned message."
}

print("Submitting pin")
r = requests.post(url, headers=headers, json=pin_json)
print(r.text)
time.sleep(5)

comp_json = {
    "name": "comp",
    "type": 1,
    "description": "Create or adjust complication dice.",
    "options": [
        {
            "name": "add",
            "description": "Create a complication die.",
            "type": 1,
            "options": [
                {
                    "name": "dice",
                    "description": "Complication dice and name.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "stepup",
            "description": "Step up the complication.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Complication name.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "stepdown",
            "description": "Step down the complication.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Complication name.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove the complication.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Complication name.",
                    "type": 3,
                    "required": True
                }
            ]
        }
    ]
}

print("Submitting comp")
r = requests.post(url, headers=headers, json=comp_json)
print(r.text)
time.sleep(5)

pp_json = {
    "name": "pp",
    "type": 1,
    "description": "Award or remove plot points.",
    "options": [
        {
            "name": "add",
            "description": "Give plot points.",
            "type": 1,
            "options": [
                {
                    "name": "number",
                    "description": "How many plot points.",
                    "type": 4,
                    "required": True
                },
                {
                    "name": "name",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove or spend plot points.",
            "type": 1,
            "options": [
                {
                    "name": "number",
                    "description": "How many plot points.",
                    "type": 4,
                    "required": True
                },
                {
                    "name": "name",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "clear",
            "description": "Remove all plot points for character or player.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                }
            ]
        }
    ]
}

print("Submitting pp")
r = requests.post(url, headers=headers, json=pp_json)
print(r.text)
time.sleep(5)

roll_json = {
    "name": "roll",
    "type": 1,
    "description": "Roll some dice",
    "options": [
        {
            "name": "dice",
            "description": "The dice to roll",
            "type": 3,
            "required": True
        }
    ]
}

print("Submitting roll")
r = requests.post(url, headers=headers, json=roll_json)
print(r.text)
time.sleep(5)

pool_json = {
    "name": "pool",
    "type": 1,
    "description": "Update or roll a dice pool.",
    "options": [
        {
            "name": "add",
            "description": "Add dice to a pool.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the dice pool.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "dice",
                    "description": "Dice to add to the pool.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove dice from a pool.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the dice pool.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "dice",
                    "description": "Dice to remove from the pool.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "roll",
            "description": "Roll the dice in a pool.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the dice pool.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "dice",
                    "description": "Extra dice to include in this roll.",
                    "type": 3
                }
            ]
        },
        {
            "name": "clear",
            "description": "Remove an entire pool.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the dice pool",
                    "type": 3,
                    "required": True
                }
            ]
        }
    ]
}

print("Submitting pool")
r = requests.post(url, headers=headers, json=pool_json)
print(r.text)
time.sleep(5)

stress_json = {
    "name": "stress",
    "type": 1,
    "description": "Create or adjust stress dice.",
    "options": [
        {
            "name": "add",
            "description": "Add a stress die.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "dice",
                    "description": "Die size.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "type",
                    "description": "The type of stress.",
                    "type": 3
                }
            ]
        },
        {
            "name": "stepup",
            "description": "Step up a stress die.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "type",
                    "description": "The type of stress.",
                    "type": 3
                }
            ]
        },
        {
            "name": "stepdown",
            "description": "Step down a stress die.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "type",
                    "description": "The type of stress.",
                    "type": 3
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove one stress die.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "type",
                    "description": "The type of stress.",
                    "type": 3
                }
            ]
        },
        {
            "name": "clear",
            "description": "Remove all stress for a player or character.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                }
            ]
        }
    ]
}

print("Submitting stress")
r = requests.post(url, headers=headers, json=stress_json)
print(r.text)
time.sleep(5)

asset_json = {
    "name": "asset",
    "type": 1,
    "description": "Create or adjust asset dice.",
    "options": [
        {
            "name": "add",
            "description": "Add an asset die.",
            "type": 1,
            "options": [
                {
                    "name": "die",
                    "description": "Die size.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "name",
                    "description": "The name of the asset.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "stepup",
            "description": "Step up an asset.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "The name of the asset.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "stepdown",
            "description": "Step down an asset.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "The name of the asset.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove an asset.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "The name of the asset.",
                    "type": 3,
                    "required": True
                }
            ]
        }
    ]
}

print("Submitting asset")
r = requests.post(url, headers=headers, json=asset_json)
print(r.text)
time.sleep(5)

xp_json = {
    "name": "xp",
    "type": 1,
    "description": "Award or remove experience points."
}

clean_json = {
    "name": "clean",
    "type": 1,
    "description": "Clean all game information from this channel."
}

report_json = {
    "name": "report",
    "type": 1,
    "description": "Show CortexPal2000's usage statistics."
}

option_json = {
    "name": "option",
    "type": 1,
    "description": "Modify CortexPal2000's options for this channel."
}


