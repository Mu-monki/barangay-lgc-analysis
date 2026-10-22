import pandas as pd
import geopandas as gpd
import re

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).upper().strip()
    
    # 1. Fix the corrupted "Ñ" encoding from the GIS file
    text = text.replace('Ã‘', 'Ñ').replace('Ã±', 'Ñ')
    
    # 2. Strip out parentheses (e.g., "New Era (Constitution Hills)" -> "New Era")
    text = re.sub(r'\(.*?\)', '', text)
    
    # Standardize prefixes
    text = re.sub(r'^CITY OF ', '', text)
    text = re.sub(r' CITY$', '', text)
    text = re.sub(r'^BRGY\.?\s*', '', text)
    text = re.sub(r'^BARANGAY\s+', 'BARANGAY ', text)
    
    text = re.sub(r'[^\w\s]', '', text) 
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def merge_population_to_shapefile(csv_path, shp_path, output_shp_path):
    print("Loading datasets...")
    df_pop = pd.read_csv(csv_path)
    gdf_map = gpd.read_file(shp_path)
    
    print("Sanitizing text...")
    df_pop['match_mun'] = df_pop['City/Municipality'].apply(clean_text)
    df_pop['match_bgy'] = df_pop['Barangay'].apply(clean_text)
    gdf_map['match_mun'] = gdf_map['Mun_Name'].apply(clean_text)
    gdf_map['match_bgy'] = gdf_map['Bgy_Name'].apply(clean_text)
    
    # --- THE OVERRIDE DICTIONARY ---
    # 1. Force all Manila districts in the GIS map to simply be "MANILA"
    manila_districts = ['TONDO I  II', 'SAMPALOC', 'SANTA CRUZ', 'SANTA ANA', 'BINONDO', 
                        'ERMITA', 'INTRAMUROS', 'MALATE', 'PACO', 'PANDACAN', 'PORT AREA', 
                        'QUIAPO', 'SAN MIGUEL', 'SAN NICOLAS']
    gdf_map.loc[gdf_map['match_mun'].isin(manila_districts), 'match_mun'] = 'MANILA'
    
    # 2. Force the EMBO barangays in the GIS map to be under "TAGUIG" instead of "MAKATI"
    embo_brgys = ['CEMBO', 'COMEMBO', 'EAST REMBO', 'PEMBO', 'PITOGO', 
                  'POST PROPER NORTHSIDE', 'POST PROPER SOUTHSIDE', 
                  'SOUTH CEMBO', 'WEST REMBO', 'RIZAL']
    gdf_map.loc[gdf_map['match_bgy'].isin(embo_brgys), 'match_mun'] = 'TAGUIG'
    
    print("Executing composite join...")
    # Perform the merge
    merged_gdf = gdf_map.merge(
        df_pop[['match_mun', 'match_bgy', 'Population']], 
        on=['match_mun', 'match_bgy'], 
        how='left'
    )
    
    # --- FILTER FOR NCR ONLY ---
    # Since we only have NCR data, let's drop the rest of the Philippines 
    # to clean up your GIS file for the paper.
    ncr_gdf = merged_gdf[merged_gdf['Population'].notna()].copy()
    
    # Find any NCR barangays from the CSV that still failed to match the map
    # (Doing a right merge to see what population data got left behind)
    test_merge = df_pop.merge(gdf_map, on=['match_mun', 'match_bgy'], how='left')
    true_unmatched = test_merge[test_merge['Mun_Name'].isna()]
    
    print(f"\nJoin Complete! Successfully matched {len(ncr_gdf)} NCR barangays.")
    
    if not true_unmatched.empty:
        true_unmatched[['City/Municipality', 'Barangay']].to_csv("true_ncr_failures.csv", index=False)
        print(f"Saved {len(true_unmatched)} stubborn NCR mismatches to 'true_ncr_failures.csv'.")
    
    # Clean up columns and save
    ncr_gdf = ncr_gdf.drop(columns=['match_mun', 'match_bgy'])
    ncr_gdf.to_file(output_shp_path)
    print(f"\nSuccess! NCR-only shapefile saved to: {output_shp_path}")

# --- EXECUTION ---
# Replace these with your actual file names
csv_file = "sanitized_master_population.csv"
shapefile_input = "gis/IMTWG_BarangayCOD_superfinal_utm.shp" 
shapefile_output = "barangay_map_with_population.shp"

merge_population_to_shapefile(csv_file, shapefile_input, shapefile_output)
