import pandas as pd

def prove_urban_fragmentation():
    filename = "comprehensive_systemic_accessibility.csv"
    
    print(f"Loading data from {filename}...\n")
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print("Error: Could not find the CSV file.")
        return

    # Group by the Service Accessibility Index Score
    summary = df.groupby('SAI_Score').agg(
        Barangay_Count=('SAI_Score', 'count'),
        Avg_Area_sqkm=('area_sqkm', 'mean'),
        Total_Area_sqkm=('area_sqkm', 'sum')
    ).reset_index()
    
    # Calculate percentages to show the disparity
    total_count = summary['Barangay_Count'].sum()
    total_area = summary['Total_Area_sqkm'].sum()
    
    summary['%_of_Total_Count'] = (summary['Barangay_Count'] / total_count * 100).round(1)
    summary['%_of_Total_Landmass'] = (summary['Total_Area_sqkm'] / total_area * 100).round(1)
    
    # Clean up the float for readability
    summary['Avg_Area_sqkm'] = summary['Avg_Area_sqkm'].round(2)
    summary['Total_Area_sqkm'] = summary['Total_Area_sqkm'].round(1)

    print("--- SPATIAL FOOTPRINT BY SAI SCORE ---")
    print(summary.to_string(index=False))
    
    print("\n--- HYPOTHESIS CONCLUSION ---")
    score_4_avg = summary.loc[summary['SAI_Score'] == 4, 'Avg_Area_sqkm'].values[0]
    score_2_avg = summary.loc[summary['SAI_Score'] == 2, 'Avg_Area_sqkm'].values[0]
    
    print(f"A Score 4 barangay is, on average, {score_4_avg} sq km.")
    print(f"A Score 2 barangay is, on average, {score_2_avg} sq km.")
    
    if score_2_avg > score_4_avg:
        multiplier = round(score_2_avg / score_4_avg, 1)
        print(f"Result: Your hypothesis is correct. Lower-scoring barangays are {multiplier}x larger than fully serviced urban barangays.")

if __name__ == "__main__":
    prove_urban_fragmentation()