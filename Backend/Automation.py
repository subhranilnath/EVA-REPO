# Import required libraries
from AppOpener import close, open as appopen  # Open or close installed applications
from pywhatkit import search, playonyt  # Google search and YouTube playback
from dotenv import dotenv_values  # Load variables from .env file
from bs4 import BeautifulSoup  # HTML parser for scraping search result links
from rich import print  # Rich text formatting in terminal
from groq import Groq  # Interface with Groq AI models
import webbrowser  # Open URLs in browser
import subprocess  # Run local applications
import requests  # HTTP requests
import keyboard  # Simulate keyboard inputs
import asyncio  # Run asynchronous tasks
import os  # Interact with operating system
import json  # Handle JSON files

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Safely fetch Groq API Key

# Define list of CSS classes that may appear in search result content blocks
classes = ["zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLCW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq API client with API key
client = Groq(api_key=GroqAPIKey)

# Standard polite replies used by AI when responding
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask."
]
messages = []  # Stores ongoing conversation for context

# Set up system prompt for Groq assistant's role
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Load cached game paths from file to avoid repeated drive scans
def load_cached_games():
    if os.path.exists("game_paths.json"):
        with open("game_paths.json", "r") as f:
            return json.load(f)
    return {}

# Save discovered game paths to cache for future use
def save_cached_games(game_paths):
    with open("game_paths.json", "w") as f:
        json.dump(game_paths, f, indent=4)

# Scan local drives to find game .exe files based on app name
# Uses early return if 3+ matches are found to save time
def find_game_exe(app_name, search_paths=["C:\\", "D:\\", "E:\\"]):
    matches = []
    app_name = app_name.lower().replace(" ", "")
    excluded_dirs = ["$recycle.bin", "windows", "programdata", "system volume information"]

    for root_dir in search_paths:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if all(x not in d.lower() for x in excluded_dirs)]
            for file in files:
                if file.lower().endswith(".exe") and app_name in file.lower().replace(" ", ""):
                    full_path = os.path.join(root, file)
                    matches.append(full_path)
                    if len(matches) >= 3:
                        return matches
    return matches

# Perform a Google search using pywhatkit
def GoogleSearch(Topic):
    search(Topic)
    return True

# Generate creative content via AI and open in notepad
def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f" {prompt}"})
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic: str = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)
    with open(rf"Data\{Topic.lower().replace('', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()
        OpenNotepad(rf"Data\{Topic.lower().replace('', '')}.txt")
        return True

# Open YouTube with search query in browser
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Play YouTube video using pywhatkit
def PlayYoutube(query):
    playonyt(query)
    return True

# Main method to launch apps, games, or websites
def OpenApp(app, sess=requests.session()):
    fallback_urls = {
        "youtube": "https://www.youtube.com",
        "instagram": "https://www.instagram.com",
        "whatsapp": "https://web.whatsapp.com",
        "facebook": "https://www.facebook.com",
        "brave": "https://www.brave.com/",
        "canva": "https://www.canva.com/",
        "telegram": "https://web.telegram.org/",
    }

    def extract_links(html):
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.select('a[href^="/url?q="]')
        return [link.get('href').split('&')[0].replace("/url?q=", "") for link in links if link.get('href')]

    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": useragent}
        response = sess.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None

    app_key = app.lower().strip()
    found_in_fallback = app_key in fallback_urls

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"[green]App opened using AppOpener:[/green] {app}")
        return True
    except:
        print(f"[yellow]AppOpener failed for:[/yellow] {app}")

    if found_in_fallback:
        webbrowser.open(fallback_urls[app_key])
        print(f"[blue]Opened fallback URL for:[/blue] {app}")
        return True

    html = search_google(app)
    links = extract_links(html)
    if links:
        webbrowser.open(links[0])
        print(f"[blue]Opened search result for:[/blue] {app}")
        return True

    cached_paths = load_cached_games()
    game_key = app.lower().replace(" ", "")

    if game_key in cached_paths:
        try:
            subprocess.Popen(cached_paths[game_key])
            print(f"[green]Launching cached game:[/green] {cached_paths[game_key]}")
            return True
        except:
            print(f"[yellow]Cached path failed. Re-scanning...[/yellow]")

    print(f"[blue]Searching for {app}.exe in local drives...[/blue]")
    matches = find_game_exe(app)

    if matches:
        exe_path = matches[0]
        cached_paths[game_key] = exe_path
        save_cached_games(cached_paths)
        subprocess.Popen(exe_path)
        print(f"[green]Found and launched:[/green] {exe_path}")
        return True
    else:
        print(f"[red]Game .exe for '{app}' not found in system.[/red]")
        return GoogleSearch(app)

# Close apps using AppOpener or pass if it's Chrome
# Ignores Chrome intentionally to prevent accidental shutdown
def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

# Adjust system volume using simulated keyboard keys
def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

# Parse and asynchronously execute multiple commands
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            if "open it" in command or "open file" == command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass
        elif command.startswith("close"):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content"):
            fun = asyncio.to_thread(Content, command.removeprefix("content"))
            funcs.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No Function Found. For {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# Main function to execute command list asynchronously
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

# Entry point for manual testing
if __name__ == "__main__":
    asyncio.run(Automation (["google search google docs"]))