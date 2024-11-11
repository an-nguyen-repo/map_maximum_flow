import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import folium
from config import KEY_LOCATIONS, LOCATION_CENTROID, MAP_RADIUS
import json 
# Configure osmnx
ox.config(use_cache=True, log_console=True)

class RoadNetworkExtractor:
    def __init__(self):
        # Key locations in HCMC (latitude, longitude)
        self.key_locations = KEY_LOCATIONS
        # Center point of our area of interest
        self.center_point = LOCATION_CENTROID
        
    def extract_road_network(self, distance: int = 500) -> nx.MultiDiGraph:
        """Extract road network within specified distance (in meters) from center point

        Args:
            distance (int, optional): Defaults to 500.

        Returns:
            nx.MultiDiGraph: 
                Multi: each nodes could have mutiple edges 
                Di: Direction is allow a->b is different from b-> a 
        """
        # Get driving network with geometries included
        G = ox.graph_from_point(
            self.center_point,
            dist=distance,
            dist_type= 'network',
            network_type='drive',
            simplify=True,
            retain_all=False,
            truncate_by_edge=True
        )
        # Print network stats
        print(f"Network extracted with {len(G.nodes)} nodes and {len(G.edges)} edges")

        # Project network to UTM
        G = ox.project_graph(G)

        return G
    
    @staticmethod
    def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate the Haversine distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert latitude and longitude to radians
        lat1, lon1 = np.radians([lat1, lon1])
        lat2, lon2 = np.radians([lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def get_nearest_nodes(self, G: nx.MultiDiGraph) -> Dict[str, int]:
        """Find the nearest nodes with additional debugging information"""
        nearest_nodes = {}
        
        # First, unproject graph to get lat/lon coordinates
        G = ox.project_graph(G, to_crs='EPSG:4326')
        
        for name, data in self.key_locations.items():
            # Get nearest node
            coords = data['coords']
            nearest_node = ox.nearest_nodes(G, coords[1], coords[0])
            self.key_locations[name]['node_id'] = nearest_node
            # Get the coordinates of the nearest node
            node_coords = (G.nodes[nearest_node]['y'], G.nodes[nearest_node]['x'])
            
            # Calculate distance to nearest node
            dist = self.haversine_distance(coords, node_coords)
            
            print(f"\nLocation: {name}")
            print(f"Original coordinates: {coords}")
            print(f"Nearest node: {nearest_node}")
            print(f"Nearest node coordinates: {node_coords}")
            print(f"Distance to nearest node: {dist:.2f} km")
            
            nearest_nodes[name] = nearest_node
            
        return nearest_nodes

    
    def add_capacity_estimates(self, G: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """Add estimated road capacity based on road type * number of lanes 

        Args:
            G (nx.MultiDiGraph): Each edges in the graph as an highway attributes that stores
            the type of road, ranked with the order defined in capacity_rules dictionary.
            For example, 'motorway' is High-speed highways/freeways and 'trunk' are Major arterial roads.
            For HCMC, most common road types would be residential, unclassified, tertiary

        Returns:
            nx.MultiDiGraph
        """

        # Rough capacity estimates (vehicles per hour per lane)
        capacity_rules = {
            'motorway': 2000,
            'trunk': 1800,
            'primary': 1600,
            'secondary': 1400,
            'tertiary': 1200,
            'residential': 800,
            'unclassified': 600
        }
        
        for u, v, k, data in G.edges(keys=True, data=True):
            # Get road type
            highway = data.get('highway', 'unclassified')
            if isinstance(highway, list):
                highway = highway[0]
                
            # Estimate number of lanes (if not available)
            lanes = data.get('lanes', 2)
            if isinstance(lanes, list):
                lanes = int(lanes[0])
            elif isinstance(lanes, str):
                lanes = int(lanes)
            else:
                lanes = 1
            
            # Calculate capacity
            base_capacity = capacity_rules.get(highway, 600)
            total_capacity = base_capacity * lanes
            
            # Add capacity to edge attributes
            G.edges[u, v, k]['capacity'] = total_capacity
            
        return G
    
    
    def create_matrix_representation(self, G: nx.MultiDiGraph, ):
        """Create an adjacency matrix from the graph with calculated capacities as weights

        Args:
            G (nx.MultiDiGraph)

        """
        node_index_lookup = {}
        node_name_lookup = {}
        seen_node_name = set()
        nodes = list(G.nodes())
        #key_location_name:
        for loc, loc_data in self.key_locations.items():
            node_name_lookup[loc_data['name']] = loc_data['node_id']
            seen_node_name.add(loc_data['node_id'])
        for idx, node_id in enumerate(nodes):
            # node index lookup
            node_index_lookup[node_id] = idx 
            # node name look up 
            if node_id not in seen_node_name:
                neighbors = list(G.neighbors(node_id))
                edge_name = ''
                if neighbors:
                    first_neighbor_id = neighbors[0]
                    edge_data = G.get_edge_data(node_id, first_neighbor_id)[0]
                    edge_name = edge_data.get('name', '')
                    if edge_name is not None  and isinstance(edge_name, list):
                        edge_name = edge_name[0]
                    node_name = edge_name +f'#{node_id}'
                else:
                    node_name = edge_name +f'#{node_id}'
                node_name_lookup[node_name] = node_id
                seen_node_name.add(node_id)

        # build adjacent matrix 
        n = len(nodes)
        matrix = [[0 for _ in range(n)] for _ in range(n)]

        for i , node1 in enumerate(nodes):
            for j , node2 in enumerate(nodes):
                edges = G.get_edge_data(node1, node2, default=None )
                if edges is not None:
                    matrix[i][j] = edges[0].get('capacity')

        self.node_name_lookup = node_name_lookup
        self.node_index_lookup = node_index_lookup
        self.adj_matrix = matrix 
        return matrix, node_name_lookup, node_index_lookup

    
    def visualize_network(self, G: nx.MultiDiGraph, ) -> folium.Map:
        """Create a Folium map visualization of the road network

        Args:
            G (nx.MultiDiGraph): _description_

        Returns:
            folium.Map: _description_
        """
        # Create base map
        m = folium.Map(location=self.center_point, zoom_start=13)
        
        # Add markers for key locations
        for name, data in self.key_locations.items():
            coords = data['coords']
            folium.Marker(
                coords,
                popup=name.replace('_', ' ').title(),
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
                
        return m
    
    def save_data(self, filename: str = 'road_network_data.json'):
        """
        Save the adjacency matrix and node data
        """
        data = {
            'adjacent_matrix' : self.adj_matrix,
            'node_name_lookup': self.node_name_lookup,
            'node_index_lookup': self.node_index_lookup,
            'nodes': list(self.node_index_lookup.keys()),
            'key_locations': self.key_locations,
            'center_point': self.center_point
        }

        with open(filename, 'w+', encoding='utf-8') as file:
            file.write(json.dumps(data, ensure_ascii= False))

    def execute(self):
        # Create extractor instance
        extractor = RoadNetworkExtractor()
        try:
            # Extract road network
            print("Extracting road network...")
            G = extractor.extract_road_network(distance=MAP_RADIUS)
            
            # Add capacity estimates
            print("Adding capacity estimates...")
            G = extractor.add_capacity_estimates(G)
            
            # Get nearest nodes to key locations
            print("Finding nearest nodes...")
            nearest_nodes = extractor.get_nearest_nodes(G)
            
            # Create adjacency matrix
            print("Creating adjacency matrix...")
            adj_matrix, node_name_lookup, node_index_lookup = extractor.create_matrix_representation(G, )
            
            # Save data
            print("Saving data...")
            extractor.save_data()
            ox.save_graphml(G, 'road_network.graphml')
            # Create visualization
            print("Creating visualization...")
            m = extractor.visualize_network(G, )
            m.save('road_network_visualization.html')
            
            print(f"Network has {len(G.nodes())} nodes and {G.number_of_edges()} edges")
            print("Data collection completed!")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise


if __name__ == "__main__":
    e = RoadNetworkExtractor()
    e.execute()