import pandas as pd

def update_regional_compliance():
    input_csv = "lgc_tagged_for_qgis.csv"
    output_csv = "lgc_regional_compliance.csv"

    print(f"Loading dataset: '{input_csv}'...")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_csv}'.")
        return

    # 1. PSGC Region Mapping Dictionary
    # Maps the numeric 'reg' codes to their official administrative names
    region_map = {
        1: 'Region I (Ilocos)', 
        2: 'Region II (Cagayan Valley)', 
        3: 'Region III (Central Luzon)', 
        4: 'Region IV-A (CALABARZON)',
        5: 'Region V (Bicol)', 
        6: 'Region VI (Western Visayas)', 
        7: 'Region VII (Central Visayas)', 
        8: 'Region VIII (Eastern Visayas)', 
        9: 'Region IX (Zamboanga Peninsula)', 
        10: 'Region X (Northern Mindanao)', 
        11: 'Region XI (Davao)', 
        12: 'Region XII (SOCCSKSARGEN)', 
        13: 'NCR (Metro Manila)', 
        14: 'CAR (Cordillera)', 
        16: 'Region XIII (Caraga)', 
        17: 'MIMAROPA', 
        18: 'NIR (Negros Island Region)', 
        19: 'BARMM'
    }

    # 2. Standardize thresholds and evaluate LGC compliance
    df['Updated_LGC_Threshold'] = df['analysis_is_metropolitan'].apply(lambda x: 5000 if x else 2000)
    df['analysis_pop_2024_cleaned'] = df['analysis_pop_2024_cleaned'].fillna(0)
    df['Is_Compliant'] = df['analysis_pop_2024_cleaned'] >= df['Updated_LGC_Threshold']

    # Map the region names
    df['Region_Name'] = df['reg'].map(region_map).fillna(df['reg'].apply(lambda x: f"Region Code {x}"))

    print("Aggregating LGC compliance by Region...\n")
    
    # 3. Group by the translated Region Name
    summary = df.groupby('Region_Name').agg(
        Total_Barangays=('code', 'count'),
        Compliant_Barangays=('Is_Compliant', 'sum')
    ).reset_index()

    # Calculate Non-Compliant counts and Compliance Rates
    summary['Non_Compliant_Barangays'] = summary['Total_Barangays'] - summary['Compliant_Barangays']
    summary['Compliance_Rate'] = (summary['Compliant_Barangays'] / summary['Total_Barangays'] * 100)

    # 4. Sort to rank the worst compliance rates at the top
    summary = summary.sort_values(by=['Compliance_Rate', 'Total_Barangays'], ascending=[True, False])

    # Calculate National Totals
    total_brgys = summary['Total_Barangays'].sum()
    total_compliant = summary['Compliant_Barangays'].sum()
    total_non_compliant = summary['Non_Compliant_Barangays'].sum()
    total_rate = (total_compliant / total_brgys) * 100

    # Format the numbers for terminal output
    summary_print = summary.copy()
    summary_print['Total_Barangays'] = summary_print['Total_Barangays'].apply(lambda x: f"{x:,}")
    summary_print['Compliant_Barangays'] = summary_print['Compliant_Barangays'].apply(lambda x: f"{x:,}")
    summary_print['Non_Compliant_Barangays'] = summary_print['Non_Compliant_Barangays'].apply(lambda x: f"{x:,}")
    summary_print['Compliance_Rate'] = summary_print['Compliance_Rate'].apply(lambda x: f"{x:.2f}%")

    print("--- REGIONAL COMPLIANCE RANKINGS (Lowest to Highest) ---")
    print(summary_print.to_string(index=False))

    print("\n" + "-" * 85)
    print(f"{'NATIONAL TOTAL':<31} {total_brgys:<16,} {total_compliant:<20,} {total_non_compliant:<20,} {total_rate:.2f}%")

    # 5. Export the readable master list
    summary.to_csv(output_csv, index=False)
    print(f"\nSuccessfully exported mapped regional ranking to '{output_csv}'")

if __name__ == "__main__":
    update_regional_compliance()