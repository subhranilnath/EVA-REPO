from Frontend.GUI import (
    GraphicalUserInterface,
    ShowTextToScreen,
    TempDirectoryPath,
    SetAssistantStatus,
    GetAssistantStatus,
    GetMicrophoneStatus,
    SetMicrophoneStatus
)
from Backend.SpeechToText import (
    SetAssistantStatus,
    QueryModifier
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import (
    RealtimeSearchEngine,
    AnswerModifier
)
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import sys

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''
subprocess_list = []  # renamed to avoid conflict with subprocess module
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]


def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)


def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


InitialExecution()


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    # Perform automation if command matches
    for queries in Decision:
        if any(queries.startswith(func) for func in Functions):
            run(Automation(Decision))
            TaskExecution = True
            break

    # Start image generation if any general query
    ImageExecution = False
    ImageGenerationQuery = None

    # Possible prefixes the model might return
    prefixes = [
        "generate image of ",
        "general generate image of ",
        "generate image ",
        "general generate image "
    ]

    for queries in Decision:
        print(f"[DEBUG] Checking query: '{queries}'")
        q_lower = queries.lower().strip()
        for p in prefixes:
            if q_lower.startswith(p):
                print(f"[DEBUG] Matched prefix: '{p}'")
                ImageGenerationQuery = queries[len(p):].strip()
                ImageExecution = True
                break
        if ImageExecution:
            break

    if ImageExecution and ImageGenerationQuery:
        print(f"[DEBUG] Final image query: '{ImageGenerationQuery}'")

        # Write to file
        image_file_path = os.path.abspath(r"Frontend\Files\ImageGeneration.data")
        os.makedirs(os.path.dirname(image_file_path), exist_ok=True)
        with open(image_file_path, "w", encoding="utf-8") as file:
            file.write(f"{ImageGenerationQuery},True")

        # Build full backend script path
        backend_script = os.path.abspath(r"Backend\ImageGeneration.py")
        SetAssistantStatus("Generating images...")
        # Start backend using same Python interpreter
        try:
            print("[DEBUG] Starting ImageGeneration.py...")
            p1 = subprocess.Popen(
                [sys.executable, backend_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocess_list = []
            subprocess_list.append(p1)
            print("[DEBUG] Backend started successfully")
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
    else:
        print("[DEBUG] No matching prefix found — backend not started")


    # Realtime + General combined or only Realtime
    if (G and R) or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    # Handle general, realtime, or exit queries
    for Queries in Decision:
        if Queries.startswith("general "):
            SetAssistantStatus("Thinking...")
            QueryFinal = Queries.replace("general ", "")
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif Queries.startswith("realtime "):
            SetAssistantStatus("Searching...")
            QueryFinal = Queries.replace("realtime ", "")
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif Queries == "exit":
            QueryFinal = "Okay, Bye!"
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            SetAssistantStatus("Answering...")
            os._exit(1)


def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")


def SecondThread():
    GraphicalUserInterface()


if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()

