from ai_client import call_ai

def main() -> None:
    prompt = "Give a short, friendly greeting and one next step suggestion for building a chatbot."
    print(call_ai(prompt))

if __name__ == "__main__":
    main()
