import os
import sys
import readline
import locale
from openai import OpenAI
from rich.console import Console
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# --- Variables ---

use_stream = True
use_markdown_format = True

api_url = os.getenv("api_url", "http://localhost:8080/v1")
api_key = os.getenv("api_key")

model = os.getenv("model", "local model")
system_prompt = os.getenv("system_prompt")
temperature = float(os.getenv("temperature", "0.7"))
top_p = float(os.getenv("top_p", "0.9"))
max_tokens = int(os.getenv("max_tokens", "4096"))

client = OpenAI(
    base_url = api_url,
    api_key = api_key
)

console = Console()

message_list = [{"role": "system", "content": system_prompt}]

# --- Prepare to initialization ---

sys.stdin.reconfigure(encoding='utf-8', errors='replace')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.error:
        pass

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
