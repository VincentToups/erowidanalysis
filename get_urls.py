import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from hashlib import sha256

def mkdir_p(path):
    """
    Creates a directory and all intermediate directories (like `mkdir -p`).
    Does nothing if the directory already exists.

    :param path: The directory path to create.
    """
    os.makedirs(path, exist_ok=True)

# Define the cache directory
CACHE_DIR = "cache"

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_and_cache_url(url):
    """Fetch URL content and cache it locally."""
    # Generate a unique filename for the URL
    hashed_filename = sha256(url.encode('utf-8')).hexdigest() + ".html"
    cached_path = os.path.join(CACHE_DIR, hashed_filename)
    
    # Check if the content is already cached
    if os.path.exists(cached_path):
        print(f"Loading content from cache: {cached_path}")
        with open(cached_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Fetch the content from the URL
    print(f"Fetching content from URL: {url}")
    response = requests.get(url, verify=False)
    response.raise_for_status()  # Raise an error for bad status codes
    
    # Save the content to the cache
    with open(cached_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return response.text

def extract_table_to_dataframe(url):
    """Extract table data from the URL and return it as a DataFrame."""
    # Fetch and cache the URL content
    html_content = fetch_and_cache_url(url)
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Create a list to store row data
    data = []

    # Find all rows in the table body
    rows = soup.select('tr.exp-list-row')
    print(f"Found {len(rows)} rows");

    for row in rows:
        # Extract data from each column
        title = row.select_one('td.exp-title a').text
        url = row.select_one('td.exp-title a').attrs['href']
        author = row.select_one('td.exp-author').text
        substance = row.select_one('td.exp-substance').text
        pub_date = row.select_one('td.exp-pubdate').text

        # Append the data as a dictionary
        data.append({
            'title': title,
            'url':url,
            'author': author,
            'substance': substance,
            'publication date': pub_date
        })

    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    return df

substances = {
    "dmt":18,
    "salvia":863
};


dfs = []
for name, value in substances.items():
    url = f"https://www.erowid.org/experiences/exp.cgi?S={value}&C=1&ShowViews=0&Cellar=0&Start=1&Max=10000"  # Replace with the actual URL
    df = extract_table_to_dataframe(url)
    df['experience'] = name;
    dfs.append(df);
    mkdir_p("derived_data");
    df.to_csv(f"derived_data/{name}_experience_urls.csv");

df = pd.concat(dfs);
df.to_csv("derived_data/experience_urls.csv");


# Example Usage

