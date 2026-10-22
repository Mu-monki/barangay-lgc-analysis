import geopandas as gpd
import pandas as pd

def calculate_pure_contiguity():
    gpkg_path = "./gis/OUTPUT.gpkg"
    layer_name = "ph_barangay_lgc_tagged_fixed"
    csv_master = "lgc_tagged_for_qgis.csv"
    output_csv = "barangay_pure_contiguity_audit.csv"

    print(f"Loading map geometries from '{layer_name}'...")
    try:
        bgy_gdf = gpd.read_file(gpkg_path, layer=layer_name)
    except Exception as e:
        print(f"Error loading map: {e}")
        return
        
    print(f"Loading demographic data from '{csv_master}'...")
    try:
        master_df = pd.read_csv(csv_master)
    except FileNotFoundError:
        print(f"Error: Could not find '{csv_master}'. Continuing with spatial data only.")
        master_df = pd.DataFrame()

    # 1. Count distinct physical parts for each barangay
    def count_parts(geom):
        if geom is None or geom.is_empty:
            return 0
        if geom.geom_type == 'Polygon':
            return 1
        if geom.geom_type == 'MultiPolygon':
            return len(geom.geoms)
        return len(list(geom.geoms)) if hasattr(geom, 'geoms') else 1

    print("Evaluating spatial contiguity...")
    bgy_gdf['Part_Count'] = bgy_gdf.geometry.apply(count_parts)
    
    # 2. Define Contiguity: 1 part = Contiguous, >1 part = Non-Contiguous
    bgy_gdf['Is_Contiguous'] = bgy_gdf['Part_Count'] == 1

    # Merge demographics if available for regional breakdowns
    id_col_map = 'PHCode_Bgy' if 'PHCode_Bgy' in bgy_gdf.columns else bgy_gdf.columns[0]
    if not master_df.empty:
        merged_gdf = bgy_gdf.merge(master_df, left_on=id_col_map, right_on='PHCode_Bgy_match', how='left')
    else:
        merged_gdf = bgy_gdf

    # 3. Calculate Summary Metrics
    total_bgys = len(merged_gdf)
    contiguous = merged_gdf['Is_Contiguous'].sum()
    non_contiguous = total_bgys - contiguous
    
    print("\n--- PURE CONTIGUITY SUMMARY ---")
    print(f"Total Barangays: {total_bgys:,}")
    print(f"Contiguous (Single Polygon): {contiguous:,}")
    print(f"Non-Contiguous (MultiPolygon): {non_contiguous:,}")
    
    if 'island_region' in merged_gdf.columns:
        print("\n--- NON-CONTIGUOUS BARANGAYS BY ISLAND GROUP ---")
        non_contig_df = merged_gdf[merged_gdf['Is_Contiguous'] == False]
        print(non_contig_df['island_region'].value_counts().to_string())

    # 4. Export the results cleanly
    export_df = merged_gdf.drop(columns='geometry', errors='ignore')
    
    # Reorder columns to put contiguity status at the front
    cols = export_df.columns.tolist()
    if 'Part_Count' in cols and 'Is_Contiguous' in cols:
        cols.insert(0, cols.pop(cols.index('Is_Contiguous')))
        cols.insert(0, cols.pop(cols.index('Part_Count')))
        export_df = export_df[cols]

    export_df.to_csv(output_csv, index=False)
    print(f"\nExported pure contiguity statuses to '{output_csv}'")

if __name__ == "__main__":
    calculate_pure_contiguity()