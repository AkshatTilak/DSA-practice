# Master Challenges Database - 110 Core Topics
# Dynamically constructed by scanning question folders.

import os
import importlib.util

CHALLENGES_DB = {}

# We know the module keys are the top-level directories:
MODULE_KEYS = ["01_DSA", "02_Data_Science_ML", "03_LLD", "04_HLD"]

# Find the workspace directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

for module in MODULE_KEYS:
    module_path = os.path.join(BASE_DIR, module)
    if not os.path.exists(module_path):
        continue
    CHALLENGES_DB[module] = {}
    
    # List subdirectories (topics) in the module
    for topic in os.listdir(module_path):
        topic_path = os.path.join(module_path, topic)
        if not os.path.isdir(topic_path) or topic.startswith(".") or topic == "__pycache__":
            continue
            
        CHALLENGES_DB[module][topic] = {}
        
        # List subdirectories (challenges) in the topic
        for challenge in os.listdir(topic_path):
            challenge_path = os.path.join(topic_path, challenge)
            if not os.path.isdir(challenge_path) or not challenge.startswith("q") or challenge == "__pycache__":
                continue
                
            info_path = os.path.join(challenge_path, "info.py")
            if os.path.exists(info_path):
                try:
                    # Dynamically load the metadata dict
                    spec = importlib.util.spec_from_file_location(f"{module}.{topic}.{challenge}.info", info_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "INFO"):
                        CHALLENGES_DB[module][topic][challenge] = mod.INFO
                except Exception as e:
                    print(f"Error loading challenge info from {info_path}: {e}")
