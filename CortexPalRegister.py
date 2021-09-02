import requests
import configparser

url = "https://discord.com/api/v8/applications/697790419035226112/commands"

info_json = {
    "name": "info",
    "type": 1,
    "description": "Show all game information for this channel."
}

pin_json = {
    "name": "pin",
    "type": 1,
    "description": "Display game information in a pinned message."
}

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
                    "type": 3
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
                    "type": 3
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
                    "type": 3
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
                    "type": 3
                {
            ]
        }
    ]
}

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
                    "type": 4
                }
            ]
        }
    ]
}

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

pool_json = {
    "name": "pool",
    "type": 1,
    "description": "Update or roll a dice pool."
}

stress_json = {
    "name": "stress",
    "type": 1,
    "description": "Create or adjust stress dice."
}

asset_json = {
    "name": "asset",
    "type": 1,
    "description": "Create or adjust asset dice."
}

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

config = configparser.ConfigParser()
config.read('cortexpal.ini')

headers = {
    "Authorization": config['discord']['token']
}

r = requests.post(url, headers=headers, json=roll_json)

