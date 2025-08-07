# Import necessary libraries.     
import asyncio
import os
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
from io import BytesIO
from time import sleep

# Load your Hugging Face API key
load_dotenv()
API_KEY = os.getenv("HuggingFaceAPIKey")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Create folder if it doesn't exist
os.makedirs("Data", exist_ok=True)

# Async call to Hugging Face 
async def query(prompt: str) -> bytes:
    payload = {"inputs": prompt}
    response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return None
    
    return response.content

# Generate multiple variations of an image
async def generate_images(prompt: str):
    tasks = []
    styled_prompt = f"{prompt}, ultra detailed, 4K resolution, cinematic lighting, high sharpness"
    
    for _ in range(4):
        task = asyncio.create_task(query(styled_prompt))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    # Save valid image bytes
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                img = Image.open(BytesIO(image_bytes))
                img.save(f"Data/{prompt.replace(' ', '_')}{i + 1}.jpg")
                print(f"Saved: Data/{prompt.replace(' ', '_')}{i + 1}.jpg")
            except Exception as e:
                print(f"Image decoding failed: {e}")

# Open saved images
def open_images(prompt: str):
    Files = [f"{prompt.replace(' ', '_')}{i}.jpg" for i in range(1, 5)]
    for jpg_file in Files:
        image_path = os.path.join("Data", jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

# Combined wrapper
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Watcher loop
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data = f.read().strip()
            if ',' not in data:
                sleep(1)
                continue

            Prompt, Status = data.split(",")
            if Status.strip().lower() == "true":
                print("Generating images...")
                GenerateImages(prompt=Prompt)

                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False,False")
                break
            else:
                sleep(1)

    except Exception as e:
        print(f"Watcher error: {e}")
        sleep(1)