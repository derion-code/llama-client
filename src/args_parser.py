import argparse
import os
from src import config
from src import client_server

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

    if prompt_arg:
            # Если prompt_arg случайно оказался существующим файлом (для обратной совместимости)
            if os.path.exists(prompt_arg) and not file_arg:
                try:
                    with open(prompt_arg, "r", encoding="utf-8") as f:
                        prompt_content += f.read()
                except Exception as e:
                    config.console.print(f"[bold red]Ошибка чтения файла:[/bold red] {e}")
                    return
            else:
                prompt_content += prompt_arg

    if file_arg:
        if os.path.exists(file_arg):
            try:
                with open(file_arg, "r", encoding="utf-8") as f:
                    file_data = f.read()
                # Оформляем файл в красивые маркдаун-блоки для модели
                prompt_content += f"Содержимое файла `{file_arg}`:\n```\n{file_data}\n```\n\n"
            except Exception as e:
                config.console.print(f"[bold red]Ошибка чтения файла:[/bold red] {e}")
                return
        else:
            config.console.print(f"[bold red]Файл не найден:[/bold red] {file_arg}")
            return

    config.message_list.append({"role": "user", "content": prompt_content})
    
    try:
        response = client_server.send_request(config.message_list, config.use_stream)

        if response is None:
            return

        if config.use_stream:
            client_server.print_stream_response(response, config.use_markdown_format, use_transient=True)
        else:
            client_server.print_response(response, config.use_markdown_format)
    except KeyboardInterrupt:
        print("\n[Generation Interrupted by user]")
