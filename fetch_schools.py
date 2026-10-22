import geopandas as gpd

def fetch_and_process_schools():
    url = "https://webgis-static.up.edu.ph/api/critical_facilities/schools.geojson"
    output_gpkg = "UP_Critical_Facilities_Schools.gpkg"
    
    print("Reading live GeoJSON from UP WebGIS...")
    # Read the data directly from the URL into a spatial dataframe
    gdf = gpd.read_file(url)
    
    print("Reprojecting to metric CRS (EPSG:32651)...")
    # Reproject from decimal degrees to meters for your routing scripts
    gdf_projected = gdf.to_crs(epsg=32651)
    
    print(f"Exporting local GeoPackage to {output_gpkg}...")
    # Save as a QGIS-ready GeoPackage
    gdf_projected.to_file(output_gpkg, driver="GPKG")
    print("Extraction complete.")

def fetch_and_process_hospitals():
    url = "https://webgis-static.up.edu.ph/api/critical_facilities/hospitals.geojson"
    output_gpkg = "UP_Critical_Facilities_Hospitals.gpkg"
    
    print("Reading live GeoJSON from UP WebGIS...")
    # Read the data directly from the URL into a spatial dataframe
    gdf = gpd.read_file(url)
    
    print("Reprojecting to metric CRS (EPSG:32651)...")
    # Reproject from decimal degrees to meters for your routing scripts
    gdf_projected = gdf.to_crs(epsg=32651)
    
    print(f"Exporting local GeoPackage to {output_gpkg}...")
    # Save as a QGIS-ready GeoPackage
    gdf_projected.to_file(output_gpkg, driver="GPKG")
    print("Extraction complete.")

def fetch_and_process_police_stations():
    url = "https://webgis-static.up.edu.ph/api/critical_facilities/police_station.geojson"
    output_gpkg = "UP_Critical_Facilities_Police_Stations.gpkg"
    
    print("Reading live GeoJSON from UP WebGIS...")
    # Read the data directly from the URL into a spatial dataframe
    gdf = gpd.read_file(url)
    
    print("Reprojecting to metric CRS (EPSG:32651)...")
    # Reproject from decimal degrees to meters for your routing scripts
    gdf_projected = gdf.to_crs(epsg=32651)
    
    print(f"Exporting local GeoPackage to {output_gpkg}...")
    # Save as a QGIS-ready GeoPackage
    gdf_projected.to_file(output_gpkg, driver="GPKG")
    print("Extraction complete.")

def fetch_and_process_fire_stations():
    url = "https://webgis-static.up.edu.ph/api/critical_facilities/fire_station.geojson"
    output_gpkg = "UP_Critical_Facilities_Fire_Stations.gpkg"
    
    print("Reading live GeoJSON from UP WebGIS...")
    # Read the data directly from the URL into a spatial dataframe
    gdf = gpd.read_file(url)
    
    print("Reprojecting to metric CRS (EPSG:32651)...")
    # Reproject from decimal degrees to meters for your routing scripts
    gdf_projected = gdf.to_crs(epsg=32651)
    
    print(f"Exporting local GeoPackage to {output_gpkg}...")
    # Save as a QGIS-ready GeoPackage
    gdf_projected.to_file(output_gpkg, driver="GPKG")
    print("Extraction complete.")

if __name__ == "__main__":
    # fetch_and_process_schools()
    # fetch_and_process_hospitals()
    # fetch_and_process_police_stations()
    fetch_and_process_fire_stations()