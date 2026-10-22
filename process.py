import json
import os

def clean_population_string(pop_val):
    """
    Safely cleans population values whether they are formatted as 
    strings with spaces/commas, raw integers, dashes, or missing entirely.
    """
    if pop_val is None:
        return 0
        
    # If the API accidentally returned a raw integer instead of a string, accept it
    if isinstance(pop_val, (int, float)):
        return int(pop_val)
        
    # Convert to string and strip outer spaces
    pop_str = str(pop_val).strip()
    
    # Handle the "-" null indicator or empty strings
    if pop_str in ["", "-"]:
        return 0
        
    # Remove internal commas and convert
    clean_str = pop_str.replace(",", "")
    
    try:
        return int(clean_str)
    except ValueError:
        print(f"  [!] Warning: Unrecognized population format '{pop_val}'. Defaulting to 0.")
        return 0

def tag_lgc_population_criteria():
    input_filename = "filtered_barangays.json"
    output_filename = "lgc_tagged_barangays.json"
    
    # Check 1: Does the input file actually exist here?
    if not os.path.exists(input_filename):
        print(f"CRITICAL ERROR: '{input_filename}' was not found.")
        print(f"Make sure you are running this script in: {os.getcwd()}")
        return
        
    print(f"Step 1: Loading data from '{input_filename}'...")
    
    # Check 2: Is the JSON valid and complete?
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            barangays = json.load(f)
    except json.JSONDecodeError:
        print(f"CRITICAL ERROR: '{input_filename}' is corrupted or incomplete. The download may have failed midway.")
        return

    print(f"Successfully loaded {len(barangays)} barangays.")
    print("Step 2: Processing LGC Criteria tags...")

    ncr_region_code = 13 
    huc_city_class = "HUC"
    tagged_count = 0

    for bgy in barangays:
        # Extract the 2024 population
        pop_2024 = 0
        for pop_data in bgy.get("populations", []):
            if pop_data.get("year") == 2024:
                pop_2024 = clean_population_string(pop_data.get("population"))
                break
        
        # Determine if it is a metropolitan area
        is_metro = (
            bgy.get("reg") == ncr_region_code or 
            bgy.get("city_class") == huc_city_class
        )
        
        # Apply the LGC criteria threshold
        threshold = 5000 if is_metro else 2000
        meets_criterion = pop_2024 >= threshold
        
        # Inject the new analytical tags directly into the barangay dictionary
        bgy["analysis_is_metropolitan"] = is_metro
        bgy["analysis_pop_2024_cleaned"] = pop_2024
        bgy["analysis_lgc_threshold"] = threshold
        bgy["analysis_meets_lgc_pop"] = meets_criterion
        
        tagged_count += 1

    print(f"Step 3: Saving {tagged_count} enriched records...")
    
    # Save the enriched dataset
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(barangays, f, indent=2)
        print(f"\nSUCCESS! File generated: '{output_filename}'")
    except Exception as e:
        print(f"CRITICAL ERROR while saving: {e}")

if __name__ == "__main__":
    tag_lgc_population_criteria()