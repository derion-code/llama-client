#!/usr/bin/env python3

import os
import readline
import locale
import argparse
import sys

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

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


# --- Command Functions --- 

def do_exit(message_list) -> bool:
    """Function to exit from client"""
    print("Exit from client")
    return True

def do_clear_screen(message_list) -> bool:
    """Clear prompt screen"""
    os.system("clear")
    return False

def do_clear_history(message_list) -> bool:
    """Clear message history"""
    message_list.clear()
    message_list.append({"role": "system", "content": system_prompt})
    return False

def do_help(message_list) -> bool:
    """Display available commands"""
    print("Available commands:")
    for cmd in commands.keys():
        print(f" - {cmd}")
    return False

def turn_stream(message_list) -> bool:
    global use_stream
    use_stream = not use_stream
    print(f"Stream:", use_stream)
    return False

def turn_markdown(message_list) -> bool:
    global use_markdown_format
    use_markdown_format = not use_markdown_format
    print(f"Markdown:", use_markdown_format)
    return False

def do_about_program(message_list) -> bool:
    """Display information about the program"""
    about_text = """
[bold green]=== Llama CLI Client ===[/bold green]
[bold]Версия:[/bold] 1.0.0 (Релиз)
[bold]Описание:[/bold] Быстрый и легковесный терминальный клиент для локальных LLM (совместим с llama.cpp).
[bold]Фичи:[/bold]
  • Динамический рендеринг Markdown прямо во время стриминга.
  • Безопасный перехват Ctrl+C для прерывания генерации.
  • Управление историей контекста и поддержка readline-инпутов.

[italic dim]Разработано с душой. Приятного использования![/italic dim]
========================
"""
    console.print(about_text)
    return False

commands = {
    "/exit": do_exit,
    "/quit": do_exit,
    "/clear": do_clear_screen,
    "/clear_history": do_clear_history,
    "/stream": turn_stream,
    "/markdown": turn_markdown,
    "/about_program": do_about_program,
    "/help": do_help
}


# --- Client-Server Functions ---

def send_request(message, use_stream):
    response = client.chat.completions.create(
        model="local model",
        messages=message_list,
        stream=use_stream
    )
    return response

def print_response(response, use_markdown_format) -> str:
    full_response = response.choices[0].message.content
    if use_markdown_format:
        console.print(Markdown(full_response))
    else:
        print(full_response)

    return full_response

def print_stream_response(response, use_markdown_format, use_transient=True) -> str:
    full_response = ""
    try:
        if use_markdown_format:
            with Live(console=console, auto_refresh=False, transient=use_transient) as live:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        full_response += token 
                        live.update(Markdown(full_response), refresh=True)
            console.print(Markdown(full_response))
        else:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token 
                    print(token, end="", flush=True)
        print("\n")
    except KeyboardInterrupt:
        print("\n[Generation interrupted by user]")
        if hasattr(response, "close"):
            response.close()

    return full_response 

def parse_args():
    parser = argparse.ArgumentParser(
        description="CLI-клиент для работы с локальной LLM."
    )
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        help="Текст промпта для разового запроса ИЛИ путь к файлу, содержимое которого нужно отправить."
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Путь к файлу, который нужно прикрепить к запросу."
    )
    return parser.parse_args()

def handle_single_prompt(prompt_arg: str, file_arg: str = None):
    prompt_content = prompt_arg

    if file_arg:
        if os.path.exists(file_arg):
            try:
                with open(file_arg, "r", encoding="utf-8") as f:
                    file_data = f.read()
                # Оформляем файл в красивые маркдаун-блоки для модели
                prompt_content += f"Содержимое файла `{file_arg}`:\n```\n{file_data}\n```\n\n"
            except Exception as e:
                console.print(f"[bold red]Ошибка чтения файла:[/bold red] {e}")
                return
        else:
            console.print(f"[bold red]Файл не найден:[/bold red] {file_arg}")
            return

    if prompt_arg:
            # Если prompt_arg случайно оказался существующим файлом (для обратной совместимости)
            if os.path.exists(prompt_arg) and not file_arg:
                try:
                    with open(prompt_arg, "r", encoding="utf-8") as f:
                        prompt_content += f.read()
                except Exception as e:
                    console.print(f"[bold red]Ошибка чтения файла:[/bold red] {e}")
                    return
            else:
                prompt_content += prompt_arg

    message_list.append({"role": "user", "content": prompt_content})
    
    try:
        response = send_request(message_list, use_stream)
        if use_stream:
            print_stream_response(response, use_markdown_format, use_transient=False)
        else:
            print_response(response, use_markdown_format)
    except KeyboardInterrupt:
        print("\n[Generation Interrupted by user]")


def main() -> None:
    args = parse_args()
    
    if args.prompt:
        handle_single_prompt(args.prompt, args.file)
        return

    print("Enter a message or /help for commands.")
    while True:
        user_message = input(">>> ")

        # Check to any message
        if not user_message.strip():
            print("Enter something.")
            continue

        # Command handler
        if user_message.startswith("/"):
            user_cmd = user_message.lower()

            if user_cmd in commands:
                should_exit = commands[user_cmd](message_list)
                if should_exit:
                    break
                else:
                    continue
            else:
                print(f"Unknown command: {user_cmd}. Type /help.")
                continue

        # Adding messages to chat history and make requests to llm-server 
        message_list.append({"role": "user", "content": user_message})
        
        response = send_request(message_list, use_stream)
        if use_stream:
            assistant_response = print_stream_response(response, use_markdown_format, use_transient=True)
        else:
            assistant_response = print_response(response, use_markdown_format)

        message_list.append({"role": "assistant", "content": assistant_response})

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        do_exit(message_list)
