from bs4 import BeautifulSoup
from hashlib import sha256
import os
import pandas as pd
import requests
import sys
import time

# Define the cache directory
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_page_content(url):
    """Fetch the HTML content of the page with caching."""
    # Generate a unique filename for the URL
    hashed_filename = sha256(url.encode('utf-8')).hexdigest() + ".html"
    cached_path = os.path.join(CACHE_DIR, hashed_filename)
    
    # Check if the content is already cached
    if os.path.exists(cached_path):
        print(f"Loading from cache: {cached_path}")
        with open(cached_path, 'r', encoding='utf-8') as f:
            return f.read()

    
    # Fetch the content from the URL
    print(f"Fetching from URL: {url}")
    response = requests.get(url, verify=False)
    response.raise_for_status()

    time.sleep(1.25);
    # Save the content to the cache
    with open(cached_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return response.text

def parse_experience_page(html):
    """Parse the HTML content of the experience page."""
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the experience account
    experience_div = soup.find('div', class_='report-text-surround')
    experience_account = ""
    for element in experience_div.contents:
        if element.name not in ['table', 'style', 'script']:
            experience_account += element.get_text(strip=True) if element.name else str(element).strip()

    # Extract dosage information
    dose_chart = []
    dose_table = soup.find('table', class_='dosechart')
    for row in dose_table.find_all('tr'):
        cells = row.find_all('td')
        dose_chart.append({
            'amount': cells[1].get_text(strip=True),
            'method': cells[2].get_text(strip=True),
            'substance': cells[3].get_text(strip=True),
        })

    # Extract demographics and metadata
    footdata = soup.find('table', class_='footdata')
    demographics = {
        'exp_year': footdata.find('td', class_='footdata-expyear').get_text(strip=True).replace('Exp Year: ', ''),
        'exp_id': footdata.find('td', class_='footdata-expid').get_text(strip=True).replace('ExpID: ', ''),
        'gender': footdata.find('td', class_='footdata-gender').get_text(strip=True).replace('Gender: ', ''),
        'age': footdata.find('td', class_='footdata-ageofexp').get_text(strip=True).replace('Age at time of experience: ', ''),
        'published': footdata.find('td', class_='footdata-pubdate').get_text(strip=True).replace('Published: ', ''),
        'views': footdata.find('td', class_='footdata-numviews').get_text(strip=True).replace('Views: ', ''),
    }

    return experience_account, dose_chart, demographics


def main():
    url_root = "https://www.erowid.org/experiences/"  # Base URL
    urls = pd.read_csv("derived_data/experience_urls.csv")  # Load experience URLs

    # DataFrames to store results
    experience_data = []
    dose_data = []

    # Loop through URLs and fetch experience data
    for tail in urls['url']:
        full_url = url_root + tail
        try:
            html = fetch_page_content(full_url)
            experience, dosage, demographics = parse_experience_page(html)

            # Add experience and demographics data
            exp_id = demographics['exp_id']
            experience_data.append({
                'experience_id': exp_id,
                'experience_account': experience,
                **demographics
            })

            # Add dosage data with indexing for multiple doses
            for idx, dose in enumerate(dosage):
                dose_data.append({
                    'experience_id': exp_id,
                    'index': idx,
                    **dose
                })
        except Exception as e:
            # Log the error to standard error
            print(f"Error processing {full_url}: {e}", file=sys.stderr)

        # Optional: Pause to prevent overwhelming the server
        time.sleep(0.1)

    # Convert lists to DataFrames
    experience_df = pd.DataFrame(experience_data)
    doses_df = pd.DataFrame(dose_data)

    # Save results to CSV files or print
    experience_df.to_csv("derived_data/experience_data.csv", index=False)
    doses_df.to_csv("derived_data/doses_data.csv", index=False)
    print("Experience and dosage data saved to 'derived_data/' directory.")

main();
