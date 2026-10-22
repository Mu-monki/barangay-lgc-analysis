import geopandas as gpd
import pandas as pd
import networkx as nx
import momepy
from scipy.spatial import cKDTree
import numpy as np

def calculate_route_distances():
    # 1. Define your file paths
    # Replace these with the actual paths to your road and hospital shapefiles
    barangays_path = "Ph_Barangays_LGC_Tagged.gpkg"
    roads_path = "philippine_roads.shp"     
    hospitals_path = "hospitals.shp"
    output_path = "Ph_Barangays_Hospital_Distances.gpkg"

    print("Loading geographic datasets...")
    # Load and immediately reproject to UTM Zone 51N (EPSG:32651) 
    # This is critical so distances are calculated in meters, not decimal degrees.
    try:
        barangays = gpd.read_file(barangays_path).to_crs(epsg=32651)
        roads = gpd.read_file(roads_path).to_crs(epsg=32651)
        hospitals = gpd.read_file(hospitals_path).to_crs(epsg=32651)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # 2. Prepare the Road Network Graph
    print("Building road network graph (This may take a minute on large road files)...")
    # Ensure every road segment has a calculated length in meters
    roads['length'] = roads.geometry.length
    
    # Convert the LineString shapefile into a NetworkX graph
    # Nodes will be represented by their (x, y) coordinate tuples
    G = momepy.gdf_to_nx(roads, approach='primal', length='length')
    
    # Extract the physical node coordinates to build a KD-Tree for hyper-fast snapping
    node_coords = list(G.nodes)
    tree = cKDTree(node_coords)

    # 3. Snap Hospitals to the Network
    print("Snapping hospitals to the nearest roads...")
    hosp_coords = [(geom.x, geom.y) for geom in hospitals.geometry]
    
    # Query the KD-Tree to find the closest road node for every hospital
    _, hosp_node_indices = tree.query(hosp_coords)
    hosp_nodes = set([node_coords[i] for i in hosp_node_indices])

    # 4. Multi-Source Dijkstra's Algorithm
    print("Calculating shortest routes across the network...")
    # This floods the network from ALL hospitals simultaneously. 
    # It returns a dictionary mapping every reachable intersection to its nearest hospital.
    dist_dict = nx.multi_source_dijkstra_path_length(G, hosp_nodes, weight='length')

    # 5. Snap Barangay Centroids and Assign Distances
    print("Snapping barangay centroids and mapping route distances...")
    # Extract centroids safely using the projected geometry
    bgy_centroids = [(geom.x, geom.y) for geom in barangays.geometry.centroid]
    
    distances_m = []
    
    for coord in bgy_centroids:
        # Find the road node closest to the center of the barangay
        _, idx = tree.query(coord)
        nearest_node = node_coords[idx]
        
        # Retrieve the network distance. 
        # If the island has roads but no hospitals, the node won't exist in dist_dict.
        route_dist = dist_dict.get(nearest_node, None)
        distances_m.append(route_dist)

    # Convert meters to kilometers and add to the dataframe
    barangays['route_dist_to_hosp_m'] = distances_m
    barangays['route_dist_to_hosp_km'] = [d / 1000 if d is not None else None for d in distances_m]

    # 6. Export Results
    print(f"Exporting routed map to {output_path}...")
    barangays.to_file(output_path, driver="GPKG")
    
    # Terminal Summary
    unreachable = barangays['route_dist_to_hosp_km'].isna().sum()
    print("\n--- ROUTING SUMMARY ---")
    print(f"Total Barangays Analyzed: {len(barangays)}")
    print(f"Successfully Routed: {len(barangays) - unreachable}")
    print(f"Unreachable Barangays (Disconnected Islands/Roads): {unreachable}")

if __name__ == "__main__":
    calculate_route_distances()