import requests
import json
import time
import os
from dotenv import load_dotenv

def fetch_filtered_barangays(api_url, api_token, bgy=None, mun=None, prv=None, reg=None, page_size=100):
    """
    Fetches paginated barangay data using specific geographic filters and a URL token.
    """
    all_barangays = []
    page = 1
    
    print(f"Starting data collection from: {api_url}")
    
    while True:
        # Add the token directly to the query parameters
        params = {
            "token": api_token,
            "page": page,
            "page_size": page_size
        }
        
        # Add any geographic filters if they are provided
        if bgy: params["bgy"] = bgy
        if mun: params["mun"] = mun
        if prv: params["prv"] = prv
        if reg: params["reg"] = reg

        print(f"Fetching page {page}...")
        
        # Make the GET request without the Authorization header
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get('results', []) or data.get('data', [])
            else:
                print("Unexpected data format returned by the API.")
                break
                
            if not items:
                print("No more data found. Finished paginating.")
                break
                
            all_barangays.extend(items)
            
            if len(items) < page_size:
                print("Reached the last page of results.")
                break
                
            page += 1
            time.sleep(0.5) 
            
        else:
            print(f"Failed to fetch page {page}. HTTP Status: {response.status_code}")
            print(f"Error detail: {response.text}")
            break
            
    return all_barangays

def main():
    load_dotenv()
    
    base_url = os.getenv('PSA_API_BASE_URL')
    api_version = os.getenv('PSA_API_VERSION')
    api_token = os.getenv('PSA_API_TOKEN')
    
    if not base_url or not api_version or not api_token:
        print("ERROR: Missing environment variables.")
        return
    
    base_url = base_url.rstrip('/')
    target_api_url = f"{base_url}/psgc/{api_version}/barangays"
    
    start_time = time.time()
    
    print("Step 1: Paginating through API (Fetching all barangays)...")
    
    # Notice we removed the prv filter so it pulls the entire country
    results = fetch_filtered_barangays(
        api_url=target_api_url,
        api_token=api_token,
        page_size=100 
    )
    
    print(f"\nStep 2: Saving {len(results)} barangays to file...")
    filename = "filtered_barangays.json"
    
    if results:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
            
        elapsed = round(time.time() - start_time, 2)
        print(f"Success! Data collected and saved in {elapsed} seconds to '{filename}'.")
    else:
        print("No data was saved because the result list was empty.")
        
if __name__ == "__main__":
    main()