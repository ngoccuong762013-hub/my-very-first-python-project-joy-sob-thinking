import random

def ngg(game_stats):
    secret_number = random.randint(1, 1000)
    attempts = 0
    while True:
        user_input = input("guess the number or press q to quit: ")
        if user_input.lower() == "q":
            print("goodbye!")
            return game_stats
        
        try:
            guess = int(user_input)
        except ValueError:
            print("invalid input! Please enter a number")
            continue
            
        attempts += 1
        game_stats["ngg total attempt(s)"] += 1  
        
        if guess == secret_number:
            print("you guessed it!")
            print(f"attempts: {attempts}")
            game_stats["ngg win(s)"] += 1
            return game_stats
        elif guess < secret_number:
            print("Too low!")
            game_stats["ngg miss(es)"] += 1
        else:
            print("Too high!")
            game_stats["ngg miss(es)"] += 1

def calc(history_list):
    while True:
        num1_input = input("enter first number or press q to quit: ").lower()
        if num1_input == "q":
            print("goodbye!")
            return history_list
        try:
            num1 = float(num1_input)
            break
        except ValueError:
            print("invalid number! try again. ")

    while True:
        num2_input = input("enter second number or press q to quit: ").lower()
        if num2_input == "q":
            print("goodbye!")
            return history_list
        try:
            num2 = float(num2_input)
            break
        except ValueError:
            print("invalid number! try again.")

    operation = input("enter operation (+, -, *, /): ")
    if operation == "/" and num2 == 0:
        print("learn math again! You can't divide by zero.")
        return history_list

    result = None
    if operation == "+":
        result = num1 + num2
    elif operation == "-":
        result = num1 - num2
    elif operation == "*":
        result = num1 * num2
    elif operation == "/":
        result = num1 / num2 
    else:
        print("i don't know about this dawg")
        return history_list 

    if result is not None:
        calc_entry = f"{num1} {operation} {num2} = {result}"
        print(f"the result is: {calc_entry}")
        history_list.append(calc_entry)
        if len(history_list) > 5:
            history_list.pop(0)
            
    return history_list

def show_calc_history(history_list):
    print("\n====CALC HISTORY(last only 5 btw)====")
    if not history_list:
        print("Empty. Go do some math first.")
    else:
        for i, entry in enumerate(history_list, 1):
            print(f"{i}. {entry}")

def rps(game_stats):
    user_wins = 0
    computer_wins = 0
    options = ["rock", "paper", "scissors"]
    winning_combos = [("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")]
    
    while True:
        user_input = input("type rock/paper/scissors or q to quit: ").lower()
        if user_input == "q":
            print("goodbye!")
            break
        if user_input not in options:
            print("invalid")
            continue
            
        computer_pick = random.choice(options)
        print(f"computer picked: {computer_pick}.")
        print(f"You picked: {user_input}.")
        
        if user_input == computer_pick:
            print("its a tie!")
        elif (user_input, computer_pick) in winning_combos:
            print("you won!")
            user_wins += 1 
            game_stats["rps win(s)"] += 1
        else:
            print("computer won!")
            computer_wins += 1
            game_stats["rps_comp_win(s)"] += 1
            
        print(f"You won {user_wins} time(s).")
        print(f"Computer won {computer_wins} time(s).")
        
    return game_stats

def show_stats(game_stats):
    print("\n====STATS====")
    for game, wins in game_stats.items():
        print(f"{game}: {wins}")
    if game_stats["ngg win(s)"] > 0:
        average = (game_stats["ngg total attempt(s)"] / game_stats["ngg win(s)"])
        print("average attempts:", round(average, 2))

def reset_stats(game_stats, history_list):
    confirm = input("Are you sure you want to wipe your stats and history?(y/n):").lower()
    if confirm == "y":
        for key in game_stats:
            game_stats[key] = 0
        history_list.clear()
        print("ripp stats")
    else:
        print("Reset cancelled.")
    return game_stats, history_list

words = ["python", "programming", "challenge", "developer", "algorithm"]

hangman_art = {0: (), 1: (" O ",), 2: (" O ", " | "), 3: (" O ", "/| "), 4: (" O ", "/|\\ "), 5: (" O ", "/|\\ ", "/  "), 6: (" O ", "/|\\ ", "/ \\ ")}

def display_man(wrong_guesses):
    print("*********")
    for line in hangman_art.get(wrong_guesses, ()):
        print(line)
    print("*********")

def display_hint(hint):
    print(" ".join(hint))

def display_answer(answer):
    print(" ".join(answer))

def hangman(game_stats): 
    answer = random.choice(words)
    hint = ["_"] * len(answer)
    wrong_guesses = 0
    guessed_letters = set()
    is_running = True

    max_wrong = max(hangman_art.keys())

    while is_running:
        display_man(wrong_guesses)
        display_hint(hint)
        guess = input("Guess a letter: ").lower()
        if not guess or len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        if guess in guessed_letters:
            print("You've already guessed that letter.")
            continue
        guessed_letters.add(guess)

        if guess in answer:
            for i in range(len(answer)):
                if answer[i] == guess:
                    hint[i] = guess
            if "_" not in hint:
                print("You win!")
                display_answer(list(answer))
                game_stats["hangman win(s)"] += 1 
                is_running = False
        else:
            wrong_guesses += 1
            if wrong_guesses >= max_wrong:
                display_man(wrong_guesses)
                print("You lost! The answer was:", answer)
                game_stats["hangman loss(es)"] += 1 
                is_running = False
                
    return game_stats

def set_alarm(alarm_time):
    import winsound
    import time
    
    print(f"\nAlarm initialized for {alarm_time}.")
    confirm = input("Press ENTER to activate, or type 'c' to cancel and go back to Hub: ").lower()
    if confirm == 'c':
        print("Alarm cancelled. Returning to LIL GAME HUB...")
        return

    print(f"Alarm set for {alarm_time}. Keep this running...")
    sound_file = "Never Gonna Give You Up.wav"
    
    while True:
        current_time = time.strftime("%H:%M") 
        
        if current_time == alarm_time:
            print("\nWake up son 😂😭")
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
            
            input("Press Enter to turn off the music...")
            winsound.PlaySound(None, winsound.SND_PURGE) 
            break
            
        time.sleep(5) 

if __name__ == "__main__":
    stats = {
        "ngg win(s)": 0, 
        "rps win(s)": 0, 
        "rps_comp_win(s)": 0, 
        "ngg miss(es)": 0, 
        "ngg total attempt(s)": 0,
        "hangman win(s)": 0,     
        "hangman loss(es)": 0    
    }
    calc_history = []

    while True:
        print("\n====LIL GAME HUB====")
        print("1. guessing game")
        print("2. calculator")
        print("3. rock/paper/scissors")
        print("4. hangman")
        print("5. set alarm")
        print("6. show stats")
        print("7. show calculator history(only last 5)")
        print("8. reset stats/history")
        print("9. quit")
        
        choice = input("choose an option: ")
        
        if choice == "1":
            stats = ngg(stats) 
        elif choice == "2":
            calc_history = calc(calc_history)
        elif choice == "3":
            stats = rps(stats)
        elif choice == "4":
            stats = hangman(stats) 
        elif choice == "5":
            alarm = input("Set your alarm time in HH:MM format (e.g., 07:30): ")
            set_alarm(alarm)
        elif choice == "6":
            show_stats(stats) 
        elif choice == "7":
            show_calc_history(calc_history)
        elif choice == "8":
            stats, calc_history = reset_stats(stats, calc_history)
        elif choice == "9":
            print("goodbye!")
            break
