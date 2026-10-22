import pandas as pd

def generate_priority_list():
    sai_csv = "comprehensive_systemic_accessibility.csv"
    master_csv = "lgc_tagged_for_qgis.csv"
    output_csv = "systemic_development_priority_list.csv"

    print("Loading geographic and demographic datasets...")
    try:
        sai_df = pd.read_csv(sai_csv)
        master_df = pd.read_csv(master_csv)
    except FileNotFoundError as e:
        print(f"Error: Could not find required file. {e}")
        return

    # Identify the matching ID column in the SAI dataset
    id_col = 'PHCode_Bgy' if 'PHCode_Bgy' in sai_df.columns else sai_df.columns[0]

    # Prevent column overlap suffixing (_x, _y) by keeping only unique columns from sai_df
    cols_to_use = [col for col in sai_df.columns if col not in master_df.columns or col == id_col]

    # 1. Merge the Systemic Accessibility scores with the master population data
    print("Merging SAI scores with 2024 population baselines...")
    merged_df = pd.merge(
        master_df, 
        sai_df[cols_to_use], 
        left_on='PHCode_Bgy_match', 
        right_on=id_col, 
        how='inner'
    )

    # 2. Apply the Prioritization Logic
    # Ascending SAI Score (0 is worst/highest priority)
    # Descending Population (Highest number of affected residents goes first)
    print("Applying prioritization matrix...")
    priority_df = merged_df.sort_values(
        by=['SAI_Score', 'analysis_pop_2024_cleaned'], 
        ascending=[True, False]
    )

    # 3. Clean and organize the output columns
    target_columns = [
        'PHCode_Bgy_match', 'area_name', 'island_region', 'reg', 'prv', 'mun', 
        'analysis_pop_2024_cleaned', 'analysis_meets_lgc_pop', 'SAI_Score',
        'dist_to_Police_m', 'dist_to_Fire_m', 'dist_to_Hospital_m', 'dist_to_School_m'
    ]
    
    # Filter to only keep columns that successfully merged
    final_cols = [col for col in target_columns if col in priority_df.columns]
    priority_df = priority_df[final_cols]

    # 4. Assign a strict National Priority Rank (1 = Most Critical in the Philippines)
    priority_df.insert(0, 'National_Priority_Rank', range(1, len(priority_df) + 1))

    # Calculate some quick terminal insights
    top_100 = priority_df.head(100)
    top_100_pop = top_100['analysis_pop_2024_cleaned'].sum()

    print("\n--- TOP 5 SYSTEMIC PRIORITY BARANGAYS ---")
    
    # Safely display simplified columns for the terminal preview
    preview_cols = ['National_Priority_Rank', 'area_name', 'analysis_pop_2024_cleaned', 'SAI_Score']
    # Fallback just in case area_name is still missing for any reason
    preview_cols = [c for c in preview_cols if c in priority_df.columns]
    print(priority_df[preview_cols].head(5).to_string(index=False))

    print("\n--- PRIORITY IMPACT ANALYSIS ---")
    print(f"Resolving the Top 100 highest-priority barangays alone would restore critical emergency access to {top_100_pop:,.0f} heavily isolated residents.")

    # 5. Export
    priority_df.to_csv(output_csv, index=False)
    print(f"\nSuccessfully exported the complete master priority list to '{output_csv}'")

if __name__ == "__main__":
    generate_priority_list()