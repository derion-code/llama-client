#!/usr/bin/env python3
from src import config
from src import args_parser
from src import client_server
from src import commands

def main() -> None:
    args = args_parser.parse_args()
    
    if args.prompt:
        args_parser.handle_single_prompt(args.prompt, args.file)
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

            if user_cmd in commands.commands:
                should_exit = commands.commands[user_cmd](config.message_list)
                if should_exit:
                    break
                else:
                    continue
            else:
                print(f"Unknown command: {user_cmd}. Type /help.")
                continue

        # Adding messages to chat history and make requests to llm-server 
        config.message_list.append({"role": "user", "content": user_message})
        
        response = client_server.send_request(config.message_list, config.use_stream)
        if config.use_stream:
            assistant_response = client_server.print_stream_response(response, config.use_markdown_format, use_transient=True)
        else:
            assistant_response = client_server.print_response(response, config.use_markdown_format)

        config.message_list.append({"role": "assistant", "content": assistant_response})


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        do_exit(config.message_list)
