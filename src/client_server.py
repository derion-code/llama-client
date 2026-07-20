from rich.markdown import Markdown
from rich.live import Live
from openai import APIConnectionError, AuthenticationError, NotFoundError, APIError
from src import config

# --- Client-Server Functions ---

def send_request(message, use_stream):
    try:
        return config.client.chat.completions.create(
            model=config.model,
            messages=config.message_list,
            stream=config.use_stream, 
            temperature=config.temperature,
            top_p=config.top_p,
            max_tokens=config.max_tokens,
        )
    except APIConnectionError:
        config.console.print("[bold red]Error:[/bold red] Could not connect to the LLM server. Please check if it is running.")
    except AuthenticationError:
        config.console.print("[bold red]Error:[/bold red] Authentication failed. Please check your API key.")
    except NotFoundError:
        config.console.print("[bold red]Error:[/bold red] The requested model or endpoint was not found.")
    except APIError as e:
        config.console.print(f"[bold red]API Error:[/bold red] {e}")
    
    return None

def print_response(response, use_markdown_format) -> str:
    full_response = response.choices[0].message.content
    if use_markdown_format:
        config.console.print(Markdown(full_response))
    else:
        print(full_response)

    return full_response

def print_stream_response(response, use_markdown_format, use_transient=True) -> str:
    full_response = ""
    try:
        if use_markdown_format:
            with Live(console=config.console, auto_refresh=False, transient=use_transient) as live:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        full_response += token 
                        live.update(Markdown(full_response), refresh=True)
            config.console.print(Markdown(full_response))
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
