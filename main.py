import os
import glob
import time
import pyttsx3
import requests
import pandas as pd
from jira import JIRA
from twilio.rest import Client
import speech_recognition as sr

def main_function():
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    # Extract new recordings and then delete them
    recordings = client.recordings.list()
    for recording in recordings:
        recording_id = recording.sid    
        url = f"https://api.twilio.com/{recording.uri.replace('.json', '.wav')}"
        r = requests.get(url, allow_redirects=True)
        open(f'unprocessed_recordings/{recording_id}.wav', 'wb').write(r.content)
        recording.delete()

    # Save all transcripts in a CSV file
    current_directory = os.path.dirname(os.path.realpath("__file__")) + "/"
    unprocessed_directory = os.path.join(current_directory, 'unprocessed_recordings')
    processed_directory = os.path.join(current_directory, 'processed_recordings')
    tickets_to_make_directory = os.path.join(current_directory, 'tickets_to_make')    
    tickets_to_make_file = f"{tickets_to_make_directory}/data.csv"
    wav_files = glob.glob(f"{unprocessed_directory}/*")
    for wav_file in wav_files:
        command = react_to_recording(wav_file)
        command = "" if command == None else command.lower()
        response = command
        append_ideas_to_list(response, tickets_to_make_file)
        os.rename(wav_file, wav_file.replace("unprocessed_recordings/", "processed_recordings/", ))

    # Write each record in the CSV file as a JIRA ticket
    jira_user = os.environ['JIRA_USER']
    jira_apikey = os.environ['JIRA_TOKEN']
    jira_server = os.environ['JIRA_SERVER']
    jira = JIRA(basic_auth=(jira_user, jira_apikey), options={'server': jira_server})
    df = pd.read_csv(tickets_to_make_file)
    for index, row in df.iterrows():
        idea = str(row['Ideas'])
        # Ticket        
        issue_dict = {
        'project': "DS",
        'summary': idea if len(idea) < 120 else "New Ticket",
        'description': "" if len(idea) < 120 else idea,
        'issuetype': {'name': 'Story'},
        }
        _ = jira.create_issue(issue_dict)
    tickets_made = len(wav_files)
    speak_text(f"Created {tickets_made} ticket{'s' if tickets_made != 1 else ''}")

def react_to_recording(wav_file):
    try:
        r = sr.Recognizer()        
        audio_file = sr.AudioFile(wav_file)
        with audio_file as source:
            audio = r.record(source)
        command = r.recognize_google(audio)
        print(command)
        return command
    except:
        pass

def append_ideas_to_list(text, tickets_to_make_file):
    if text == "":
        return
    try:
        df = pd.read_csv(tickets_to_make_file)
    except:
        df = pd.DataFrame({'Ideas': []})
    new_row = pd.DataFrame({'Ideas': [text]})
    df = df.append(new_row)
    df.to_csv(tickets_to_make_file, index=False)        

def speak_text(text):
    engine = pyttsx3.init()
    engine.startLoop(False)
    engine.say(text)
    engine.iterate()
    time.sleep(0.10*len(text))
    engine.endLoop()


if __name__ == "__main__":
    main_function()