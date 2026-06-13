import os
from generator import initialize_challenge
from questions_db import CHALLENGES_DB

def main():
    print("Starting full vault initialization...")
    count = 0
    for module_key in CHALLENGES_DB:
        for topic_key in CHALLENGES_DB[module_key]:
            for challenge_key in CHALLENGES_DB[module_key][topic_key]:
                success, msg = initialize_challenge(module_key, topic_key, challenge_key)
                if success:
                    count += 1
    print(f"Initialization complete. Total active challenges created: {count}")

if __name__ == "__main__":
    main()
