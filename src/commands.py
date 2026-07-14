import os
from src import config

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
    message_list.append({"role": "system", "content": config.system_prompt})
    return False

def do_help(message_list) -> bool:
    """Display available commands"""
    print("Available commands:")
    for cmd in commands.keys():
        print(f" - {cmd}")
    return False

def turn_stream(message_list) -> bool:
    config.use_stream = not config.use_stream
    print(f"Stream:", config.use_stream)
    return False

def turn_markdown(message_list) -> bool:
    config.use_markdown_format = not config.use_markdown_format
    print(f"Markdown:", config.use_markdown_format)
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
    config.console.print(about_text)
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
