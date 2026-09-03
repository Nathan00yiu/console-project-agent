import sys
from agent import graph

def main():
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