import psutil
import os
import yaml

from openai import OpenAI
from config.base_config import BASE_PATH

llm_config_path = os.path.join(BASE_PATH, "config/llm.yaml")
with open(llm_config_path, "r") as f:
    llm_config = yaml.safe_load(f)

def close_all_chrome():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == 'chrome.exe':
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Successfully deleted")
        except OSError as e:
            print(f"Error deleting file: {e}")
    else:
        print(f"File does not exist")

def call_openrouter_llm(messages):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        response = client.chat.completions.create(
            model = llm_config["model_name"],
            messages = messages,
            temperature = llm_config["temperature"],
            extra_body=llm_config["extra_body"]
        )
        return response.choices[0].message.content
    except Exception as e:
        raise