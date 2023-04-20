import requests
import configparser
import time

config = configparser.ConfigParser()
config.read('cortexpal.ini')

url = "https://discord.com/api/v8/applications/{}/commands".format(config['discord']['app_id'])
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
                    "name": "who",
                    "description": "Name of the character or player owning the complication.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "Complication name.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "die",
                    "description": "Die size.",
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
                    "name": "who",
                    "description": "Name of the character or player owning the complication.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "Complication name.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "stepdown",
            "description": "Step down the complication.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of the character or player owning the complication.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "Complication name.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove the complication.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of the character or player owning the complication.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
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
                    "name": "who",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "number",
                    "description": "How many plot points.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove or spend plot points.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "number",
                    "description": "How many plot points.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "clear",
            "description": "Remove all plot points for character or player.",
            "type": 1,
            "options": [
                {
                    "name": "who",
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
        },
        {
            "name": "keep",
            "description": "How many dice to keep",
            "type": 4,
            "min_value": 1
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
            "name": "stepup",
            "description": "Step up one of the dice in a pool.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the dice pool.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "die",
                    "description": "Size of the die to step up.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "stepdown",
            "description": "Step down one of the dice in a pool.",
            "type": 1,
            "options": [
                {
                    "name": "name",
                    "description": "Name of the dice pool.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "die",
                    "description": "Size of the die to step down.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
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
                },
                {
                    "name": "keep",
                    "description": "How many dice to keep",
                    "type": 4
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
                    "name": "who",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "The type of stress.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "die",
                    "description": "Die size.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "stepup",
            "description": "Step up a stress die.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "The type of stress.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "stepdown",
            "description": "Step down a stress die.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "The type of stress.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove one stress die.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of the character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "The type of stress.",
                    "type": 3,
                    "required": True
                }
            ]
        },
        {
            "name": "clear",
            "description": "Remove all stress for a player or character.",
            "type": 1,
            "options": [
                {
                    "name": "who",
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
                    "name": "who",
                    "description": "The character or player owning the asset.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "The name of the asset.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "die",
                    "description": "Die size.",
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
                    "name": "who",
                    "description": "The character or player owning the asset.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "The name of the asset.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "stepdown",
            "description": "Step down an asset.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "The character or player owning the asset.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "The name of the asset.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "steps",
                    "description": "How many steps.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove an asset.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "The character or player owning the asset.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
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

dist_json = {
    "name": "dist",
    "type": 1,
    "description": "Create or remove a distinction.",
    "options": [
        {
            "name": "add",
            "description": "Create a distinction.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of the character or player owning the distinction.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "Distinction name.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "die",
                    "description": "Die size.",
                    "type": 3
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove the distinction.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of the character or player owning the disinction.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "what",
                    "description": "Distinction name.",
                    "type": 3,
                    "required": True
                }
            ]
        }
    ]
}

print("Submitting dist")
r = requests.post(url, headers=headers, json=dist_json)
print(r.text)
time.sleep(5)

xp_json = {
    "name": "xp",
    "type": 1,
    "description": "Award or remove experience points.",
    "options": [
        {
            "name": "add",
            "description": "Give experience points.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "number",
                    "description": "How many experience points.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "remove",
            "description": "Remove or spend experience points.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "number",
                    "description": "How many experience points.",
                    "type": 4,
                    "min_value": 1
                }
            ]
        },
        {
            "name": "clear",
            "description": "Remove all experience points for character or player.",
            "type": 1,
            "options": [
                {
                    "name": "who",
                    "description": "Name of character or player.",
                    "type": 3,
                    "required": True
                }
            ]
        }
    ]
}

print("Submitting xp")
r = requests.post(url, headers=headers, json=xp_json)
print(r.text)
time.sleep(5)

clean_json = {
    "name": "clean",
    "type": 1,
    "description": "Clean all game information from this channel."
}

print("Submitting clean")
r = requests.post(url, headers=headers, json=clean_json)
print(r.text)
time.sleep(5)

report_json = {
    "name": "report",
    "type": 1,
    "description": "Show CortexPal2000's usage statistics."
}

print("Submitting report")
r = requests.post(url, headers=headers, json=report_json)
print(r.text)
time.sleep(5)

option_json = {
    "name": "option",
    "type": 1,
    "description": "Modify CortexPal2000's options for this channel.",
    "options": [
        {
            "name": "best",
            "description": "Whether suggestions for the best total and effect dice will appear.",
            "type": 1,
            "options": [
                {
                    "name": "switch",
                    "description": "Turn suggestions on or off.",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "on",
                            "value": "on"
                        },
                        {
                            "name": "off",
                            "value": "off"
                        }
                    ]
                }
            ]
        },
        {
            "name": "join",
            "description": "Control how other channels can participate in this channel's game.",
            "type": 1,
            "options": [
                {
                    "name": "switch",
                    "description": "Turn permissions on or off for other channels to participate.",
                    "type": 3,
                    "choices": [
                        {
                            "name": "on",
                            "value": "on"
                        },
                        {
                            "name": "off",
                            "value": "off"
                        }
                    ]
                },
                {
                    "name": "channel",
                    "description": "All commands from this channel will apply to the named channel.",
                    "type": 7
                }
            ]
        }
    ]
}

print("Submitting options")
r = requests.post(url, headers=headers, json=option_json)
print(r.text)
time.sleep(5)

help_json = {
    "name": "help",
    "type": 1,
    "description": "List the commands that CortexPal2000 supports.",
    "options": [
        {
            "name": "command",
            "description": "The command to show instructions for.",
            "type": 3,
            "choices": [
                {
                    "name": "asset",
                    "value": "asset"
                },
                {
                    "name": "clean",
                    "value": "clean"
                },
                {
                    "name": "comp",
                    "value": "comp",
                },
                {
                    "name": "info",
                    "value": "info"
                },
                {
                    "name": "option",
                    "value": "option"
                },
                {
                    "name": "pin",
                    "value": "pin"
                },
                {
                    "name": "pool",
                    "value": "pool"
                },
                {
                    "name": "pp",
                    "value": "pp"
                },
                {
                    "name": "report",
                    "value": "report"
                },
                {
                    "name": "roll",
                    "value": "roll"
                },
                {
                    "name": "stress",
                    "value": "stress"
                },
                {
                    "name": "xp",
                    "value": "xp"
                }
            ]
        }
    ]
}

print("Submitting help")
r = requests.post(url, headers=headers, json=help_json)
print(r.text)
time.sleep(5)

