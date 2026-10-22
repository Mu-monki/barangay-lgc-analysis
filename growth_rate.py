import json
import pandas as pd
import os

def clean_population_string(pop_val):
    """Safely converts string population values to integers."""
    if pop_val is None:
        return 0
    if isinstance(pop_val, (int, float)):
        return int(pop_val)
        
    pop_str = str(pop_val).strip()
    if pop_str in ["", "-"]:
        return 0
        
    clean_str = pop_str.replace(",", "")
    try:
        return int(clean_str)
    except ValueError:
        return 0

def extract_valid_populations(populations_list):
    """Extracts and sorts valid historical data points."""
    valid_pops = []
    if not populations_list:
        return valid_pops
        
    for p in populations_list:
        year = p.get('year')
        pop_val = clean_population_string(p.get('population'))
        if year and pop_val > 0: 
            valid_pops.append((year, pop_val))
            
    valid_pops.sort(key=lambda x: x[0])
    return valid_pops

def generate_growth_rate_csv():
    input_filename = "filtered_barangays.json"
    output_filename = "barangay_growth_rates.csv"
    
    if not os.path.exists(input_filename):
        print(f"ERROR: '{input_filename}' not found.")
        return
        
    print(f"Loading data from '{input_filename}'...")
    
    with open(input_filename, 'r', encoding='utf-8') as f:
        barangays = json.load(f)

    results = []
    
    # National Aggregation Variables
    national_baseline_pop = 0
    national_annual_growth_volume = 0
    valid_barangay_count = 0
    na_barangay_count = 0

    for bgy in barangays:
        psgc_code = bgy.get("correspondence_code")
        ph_code_match = f"PH{psgc_code}" if psgc_code else "UNKNOWN"
        
        pops_list = bgy.get("populations", [])
        valid_pops = extract_valid_populations(pops_list)
        
        if len(valid_pops) >= 2:
            oldest_year, oldest_pop = valid_pops[0]
            newest_year, newest_pop = valid_pops[-1]
            years_diff = newest_year - oldest_year
            
            if years_diff > 0:
                # 1. Barangay-Level Calculation
                annual_growth = (newest_pop - oldest_pop) / years_diff
                bgy_growth_rate = (annual_growth / oldest_pop) * 100
                
                # 2. National-Level Summation (Factoring out N/As)
                national_baseline_pop += oldest_pop
                national_annual_growth_volume += annual_growth
                valid_barangay_count += 1
                
                results.append({
                    "PHCode_Bgy_match": ph_code_match,
                    "area_name": bgy.get("area_name", ""),
                    "annual_growth_rate_pct": round(bgy_growth_rate, 2)
                })
            else:
                na_barangay_count += 1
                results.append({
                    "PHCode_Bgy_match": ph_code_match,
                    "area_name": bgy.get("area_name", ""),
                    "annual_growth_rate_pct": "N/A"
                })
        else:
            na_barangay_count += 1
            results.append({
                "PHCode_Bgy_match": ph_code_match,
                "area_name": bgy.get("area_name", ""),
                "annual_growth_rate_pct": "N/A"
            })

    # Export to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_filename, index=False, encoding='utf-8')
    
    # Calculate Final National Growth Rate
    if national_baseline_pop > 0:
        national_growth_rate = (national_annual_growth_volume / national_baseline_pop) * 100
    else:
        national_growth_rate = 0
        
    print(f"\n--- EXECUTION SUMMARY ---")
    print(f"Exported file: '{output_filename}'")
    print(f"Total Barangays Processed: {len(df)}")
    print(f"Valid Barangays (Included in Summation): {valid_barangay_count}")
    print(f"Invalid Barangays (N/A, Skipped): {na_barangay_count}")
    
    print(f"\n--- NATIONAL STATISTICS ---")
    print(f"Aggregate Baseline Population: {national_baseline_pop:,.0f}")
    print(f"Aggregate Annual Growth Volume: +{national_annual_growth_volume:,.0f} persons/year")
    print(f"National Annualized Linear Growth Rate: {national_growth_rate:.2f}%")

if __name__ == "__main__":
    generate_growth_rate_csv()