import os
import glob
import time
import pyttsx3
import requests
from twilio.rest import Client

def main_function():
    # # Find your Account SID and Auth Token at twilio.com/console
    # # and set the environment variables. See http://twil.io/secure
    # account_sid = os.environ['TWILIO_ACCOUNT_SID']
    # auth_token = os.environ['TWILIO_AUTH_TOKEN']
    # client = Client(account_sid, auth_token)

    # # Extract new recordings and then delete them
    # recordings = client.recordings.list()
    # for recording in recordings:
    #     recording_id = recording.sid    
    #     url = f"https://api.twilio.com/{recording.uri.replace('.json', '.wav')}"
    #     r = requests.get(url, allow_redirects=True)
    #     open(f'unprocessed_recordings/{recording_id}.wav', 'wb').write(r.content)
    #     recording.delete()

    # Convert each recording into JIRA tickets and then move it into the processed folder
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
        append_ideas_to_list(response)
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

def append_ideas_to_list(text):
    if text == "":
        return
    df = pd.read_csv(ideas_file)
    new_row = pd.DataFrame({'Ideas': [text], 'Priority': [''], 'Status': ['Backlog'], 'Notes': ['']})
    df = df.append(new_row)
    df.to_csv(ideas_file, index=False)        

def speak_text(text):
    engine = pyttsx3.init()
    engine.startLoop(False)
    engine.say(text)
    engine.iterate()
    time.sleep(0.10*len(text))
    engine.endLoop()


if __name__ == "__main__":
    main_function()