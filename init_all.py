from questions_db import CHALLENGES_DB
from generator import initialize_challenge
import time

def init_all():
    print("Initializing all challenges...")
    count = 0
    total = sum(len(CHALLENGES_DB[m][t]) for m in CHALLENGES_DB for t in CHALLENGES_DB[m])
    
    for m in CHALLENGES_DB:
        for t in CHALLENGES_DB[m]:
            for c in CHALLENGES_DB[m][t]:
                success, msg = initialize_challenge(m, t, c)
                if success:
                    count += 1
                else:
                    print(f"Failed to initialize {c}: {msg}")
    print(f"Successfully initialized {count}/{total} challenges.")

if __name__ == "__main__":
    init_all()
