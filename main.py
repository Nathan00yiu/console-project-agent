import os
import sys
from agent import graph

ENV_CONTENT = """OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
"""

def ensure_env_file():
    """Check if .env file exists; if not, create it with default configuration."""
    if not os.path.exists(".env"):
        print("Creating missing .env file with default Ollama configuration...")
        with open(".env", "w") as f:
            f.write(ENV_CONTENT)

def main():
    ensure_env_file()
    
    print("=== AI Project Manager CLI ===")
    print("Type your request or 'exit' / 'quit' to stop.\n")

    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                sys.exit(0)

            initial_state = {"user_input": user_input}
            result = graph.invoke(initial_state)
            print(result["response"])
            print()
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()