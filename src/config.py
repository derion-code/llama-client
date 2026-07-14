import sys
import readline
import locale
from openai import OpenAI
from rich.console import Console

# --- Variables ---

use_stream = True
use_markdown_format = True

api_url = "http://192.168.1.124:8080/v1"    
api_key = "None"

client = OpenAI(
    base_url = api_url,
    api_key = api_key
)

console = Console()

system_prompt = """
Ты краткий и полезный ассистент.
"""

message_list = [{"role": "system", "content": system_prompt}]


# --- Prepare to initialization ---

sys.stdin.reconfigure(encoding='utf-8', errors='replace')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
except locale.error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.error:
        pass

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
