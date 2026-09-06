from agent.loop import run_agent

if __name__ == "__main__":
    while True: 
        user_ask = input("What is your ask? : ")

        response = run_agent(user_ask)

        print(f'\n{response}\n')