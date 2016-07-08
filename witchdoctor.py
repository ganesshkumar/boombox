import os
import time
from slackclient import SlackClient
from pymongo import MongoClient

BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">:"
PLAY_COMMAND = "play"
CLEAR_COMMAND = "clear all"

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
mongo_client = MongoClient()
db = mongo_client['witchdoctor']

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + PLAY_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(CLEAR_COMMAND):
        db['playlist'].delete_many({})
        response = "Sure...I will stop playing"
    elif command.startswith(PLAY_COMMAND):
        play_list_coll = db['playlist']
        request = ' '.join(command.split(' ')[1:])
        play_list_coll.insert_one({
            "request_string": request,
            "requested_at": long(time.time())
        })
        response = 'Sure... \'' +  request+ '\' will be played after ' + str(play_list_coll.count()) + ' songs'
        
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("witchdoctor connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
