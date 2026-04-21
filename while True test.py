
print("This is a test python code! if you see this text - this work")
user_name = input("What is your name? :")
print(f"Nice to meet you {user_name}!")
while True:
    question = input("You:").lower()
    if "hello" in question:
        print(f"Hello {user_name}!")
    elif "hello!" in question:
        print(f"Hello {user_name}!")
    elif "bye!" in question:
        print("Bye!")
        break
    else:
        print("Command not founded")