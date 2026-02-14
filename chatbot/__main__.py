"""Entry point for running the chatbot: python -m chatbot [--web] [--port PORT]"""

import sys


def main():
    args = sys.argv[1:]

    if "--web" in args:
        # Web UI mode
        from chatbot.presentation.web import main as web_main
        web_main()
    else:
        # CLI mode
        from chatbot.presentation.cli import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()
