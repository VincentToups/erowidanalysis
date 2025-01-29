# Import necessary libraries
import dspy
import pandas as pd
import os
import pickle
import hashlib
from typing import List, Literal
from tqdm import tqdm

key = os.getenv("OPENAIKEY");
# Configure the language model
lm = dspy.LM("gpt-3.5-turbo",
             api_base="http://localhost:7860/v1/",
             api_key=key,
             model_type="chat")

dspy.settings.configure(lm=lm)

class Summarizer(dspy.Signature):
    """Given a drug trip report summarize the report in
    objective, clear, language. Edit out any references to the specific drug
    used. Do not name any drug in the summary. The summary should describe what the participate felt, saw,
    experienced, and whether they experienced interaction with any other
    entitities and if so, their detailed, specific, physical descriptions and detailed
    behaviors and communications. Points will be deducted if any entities are left out of the report. Do not interpret the material, but it is important to provide
    this information for each entitity which appears.

    DO NOT INCLUDE THE NAME OF THE DRUG USED IN ANY FORM. ALL REFERENCES TO THE SUBSTANCE IDENTITY SHOULD BE REMOVED OR YOU WILL LOSE POINTS.

    """
    account: str = dspy.InputField(desc="A drug trip account.")
    summary: str = dspy.OutputField(desc="A concise, objective, summary of the drug trip.")

summero = dspy.ChainOfThought(Summarizer);
def summer(account):
    r = summero(account=account);
    return {
        "reasoning":r.reasoning,
        "summary":r.summary
    }

def ensure_directory_exists(directory: str):
    os.makedirs(directory, exist_ok=True)

# Function to hash arguments for cache key
def hash_args(func_name: str, *args) -> str:
    hasher = hashlib.sha256()
    hasher.update(func_name.encode('utf-8'))
    for arg in args:
        hasher.update(str(arg).encode('utf-8'))
    return hasher.hexdigest()

# Updated disk cache function to support keyword arguments
def call_with_disk_cache(directory: str, func, *args, **kwargs):
    ensure_directory_exists(directory)
    
    # Hash arguments and keyword arguments for cache key
    hasher = hashlib.sha256()
    hasher.update(func.__name__.encode('utf-8'))
    for arg in args:
        hasher.update(str(arg).encode('utf-8'))
    for key, value in sorted(kwargs.items()):  # Sort kwargs to ensure consistent hashing
        hasher.update(f"{key}={value}".encode('utf-8'))
    
    cache_key = hasher.hexdigest()
    cache_path = os.path.join(directory, cache_key + '.pkl')

    # Check for cached result
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as cache_file:
            return pickle.load(cache_file)
    else:
        result = func(*args, **kwargs)
        with open(cache_path, 'wb') as cache_file:
            pickle.dump(result, cache_file)
        return result

# Function to clear cache directory
def clear_directory(directory: str):
    if os.path.exists(directory):
        for file in os.listdir(directory):
            os.remove(os.path.join(directory, file))

# Read data
data = pd.read_csv("derived_data/experience_data.csv")

import time
from datetime import timedelta

# Initialize variables
start_time = time.time()
total_records = len(data['experience_account'])
summaries = []
experience_id = []
cache_dir = "cache_summaries"
#clear_directory("cache_summaries")


# Loop with custom progress tracking
for i, account in enumerate(data['experience_account']):
    try:
        # Process the account
        exp_id = data["experience_id"][i]
        result = call_with_disk_cache(cache_dir, summer, account=account)
        summaries.append(result["summary"])
        experience_id.append(exp_id)

        # Calculate progress
        completed = i + 1
        remaining = total_records - completed
        percent_done = (completed / total_records) * 100
        elapsed_time = time.time() - start_time
        est_total_time = elapsed_time / completed * total_records
        est_time_left = est_total_time - elapsed_time
        time_left_str = str(timedelta(seconds=int(est_time_left)))  # Format as HH:MM:SS

        # Print progress
        print(f"Progress: {percent_done:.2f}% | Finished: {completed} | Left: {remaining} | "
              f"Estimated Time Left: {time_left_str}")

        # Print the result summary
        print("**********************************")
        print(result["summary"])
        print("**********************************")

    except Exception as e:
        print(f"Issue with {i}")
        print(e)



df = pd.DataFrame({
    "experience_id":experience_id,
    "summary":summaries}
                  )
df.to_csv("derived_data/summaries.csv");


