# Import necessary libraries
import dspy
import pandas as pd
import os
import pickle
import hashlib
from typing import List, Literal
from tqdm import tqdm

import time
from datetime import timedelta


# API key for the language model
key = os.getenv("OPENAIKEY")
# Configure the language model
lm = dspy.LM("gpt-3.5-turbo",
             api_base="http://localhost:7860/v1/",
             api_key=key,
             model_type="chat")

dspy.settings.configure(lm=lm)

# Define the ArchetypeExtraction class
class ArchetypeExtraction(dspy.Signature):
    """
    You will receive a summarized drug trip report. If the trip report includes a specific
    entity or entities which correspond roughly with the jungian archetypes, return that
    archetype in a list. Do not interpret settings or moods as entities. Only include
    entities which appear explicitly in the account. Your response should be one of
    "self", "shadow", "anima", "animus", "persona", "hero",
        "wise_old_man", "wise_old_woman", "mother", "child", 
        "trickster", "lover", "explorer", "creator", "destroyer", 
        "ruler", "caregiver", "rebel", "orphan"
    """
    account: str = dspy.InputField(desc="A summary of a drug trip experience")
    extracted_people: List[Literal[
        "self", "shadow", "anima", "animus", "persona", "hero",
        "wise_old_man", "wise_old_woman", "mother", "child", 
        "trickster", "lover", "explorer", "creator", "destroyer", 
        "ruler", "caregiver", "rebel", "orphan"
    ]] = dspy.OutputField(desc="A list of Jungian Archetypes found in the summary.")

# Create the chain of thought object
archetype_extractor_o = dspy.ChainOfThought(ArchetypeExtraction)
def archetype_extractor(account):
    r = archetype_extractor_o(account=account)
    return {
        "reasoning": r.reasoning,
        "extracted": r.extracted_people
    }

# Function to ensure directory existence
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
data = pd.read_csv("derived_data/summaries.csv")


# Initialize the archetypes list
archetypes = []
experience_id = []
cache_dir = "cache_archetype_extraction"

# Number of summaries to process
total_summaries = len(data['summary'])

# Start processing
start_time = time.time()
for i, summary in enumerate(data['summary']):
    try:
        exp_id = data["experience_id"][i]
        record_start_time = time.time()
        
        # Extract archetypes with caching
        result = call_with_disk_cache(cache_dir, archetype_extractor, account=summary)
        for p in result["extracted"]:
            archetypes.append(p)
            experience_id.append(exp_id)
        
        # Print details of the current record
        print(f"Summary: {summary}")
        print(f"Extracted Archetypes: {result['extracted']}")
        
        # Estimate time remaining
        elapsed_time = time.time() - start_time
        avg_time_per_record = elapsed_time / (i + 1)
        records_remaining = total_summaries - (i + 1)
        estimated_time_remaining = timedelta(seconds=records_remaining * avg_time_per_record)
        
        print(f"Processed {i + 1}/{total_summaries}. Estimated time remaining: {estimated_time_remaining}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Issue with record {i}: {e}")

# Save the results to a CSV
df = pd.DataFrame({
    "experience_id": experience_id,
    "archetype": archetypes
})
df.to_csv("derived_data/archetypes.csv", index=False)
