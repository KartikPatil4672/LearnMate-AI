# main.py
"""Entry point for LearnMate AI – a CLI learning tutor.

The script creates a :class:`Tutor` instance and enters a REPL loop where the user can type natural‑language requests.
It uses :mod:`colorama` to colour the output for better accessibility.
"""

import sys
from colorama import init, Fore, Style
from tutor import Tutor

def print_welcome() -> None:
    print(Fore.CYAN + Style.BRIGHT + "Welcome to LearnMate AI – your personal learning tutor!" + Style.RESET_ALL)
    print("Type your request (e.g. 'Explain quadratic formula' or 'Quiz me on photosynthesis')")
    print("Enter 'exit' or press Ctrl‑C to quit.\n")

def main() -> None:
    init(autoreset=True)  # Initialize colorama
    tutor = Tutor()
    print_welcome()
    while True:
        try:
            user_input = input(Fore.GREEN + "You: " + Style.RESET_ALL).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        response = tutor.handle_request(user_input)
        print(Fore.YELLOW + Style.BRIGHT + "LearnMate:" + Style.RESET_ALL, response)

if __name__ == "__main__":
    main()
