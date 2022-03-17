
import requests 
import json


def send_slack_message(webhook, body):
  # fix for sending to Super Admin webhook.
  # it needs to have a text field, so just stick the json string in there
  if not body.get("text",None):
    body["text"] = json.dumps(body)

  r = requests.post(url = webhook, data = json.dumps(body))
  return r

