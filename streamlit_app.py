# streamlit_app.py

import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
from maximum_flow_algorithms import Edmond_Karps, Dinic, FordFulkerson
import json 
import time 

INACTIVE_COLOR = '#A9A9A9'
ACTIVE_COLOR = '#FF5733' 

class TrafficFlowUI:

    def __init__(self):
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load the network data"""
        try:
            # Load network data
            with open('./road_network_data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)

            self.adj_matrix = data['adjacent_matrix']
            self.node_name_lookup = data['node_name_lookup']
            self.node_index_lookup = data['node_index_lookup']
            self.nodes  = data['nodes']
            self.key_locations = data['key_locations']
            self.center_point = data['center_point']
            
            # Create reverse mappings
            self.index_node_lookup = {v: int(k) for k, v in self.node_index_lookup.items()}
            self.node_id_to_name = {v: k for k, v in self.node_name_lookup.items()}
            
            # Load graph for visualization
            self.G = ox.load_graphml('road_network.graphml')
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            raise


    def draw_node(self, m, node_id,  color = INACTIVE_COLOR):
        node_data = self.G.nodes[node_id]
        latitude = node_data['lat']
        longitude = node_data['lon']
        folium.CircleMarker(
                location=[latitude, longitude],
                radius=3,  
                color=color, 
                fill=True,
                fillColor=color, 
                fillOpacity=0.8,
                weight=0.5 
            ).add_to(m)

    def draw_edge(self, m, node_fr_id, node_to_id, color = ACTIVE_COLOR):
        coordinates = [
            [self.G.nodes[node_fr_id]['lat'], self.G.nodes[node_fr_id]['lon']] ,  # lat, long
            [self.G.nodes[node_to_id]['lat'], self.G.nodes[node_to_id]['lon']]
        ]

        # Create a PolyLine
        folium.PolyLine(
            locations=coordinates,
            weight=8,
            color=color,
            opacity=0.8,
        ).add_to(m)

    

    def create_basic_map(self, paths= None ):
        """Create a basic map with locations and paths"""
        # Create base map
        center_lat = self.center_point[0]
        center_lon = self.center_point[1]
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
        
        # Add markers for key locations
        for loc_data in self.key_locations.values():
            folium.Marker(
                loc_data['coords'],
                popup=loc_data['name'],
                icon=folium.Icon(color='red')
            ).add_to(m)

        # Add markers for all nodes 
        for node_id in self.nodes:
            self.draw_node(m, node_id=node_id, )


        # DRAW path if exists 
        if paths:
            for path in paths:
                path_node = path['path']
                for idx, node_index in enumerate(path_node):
                    node_id = self.index_node_lookup.get(node_index)
                    self.draw_node(m, node_id= node_id, color = ACTIVE_COLOR)
                    if idx < (len(path_node) - 1) :
                        next_node_id = self.index_node_lookup.get(path_node[idx +1 ])
                        self.draw_edge(m, node_fr_id= node_id, node_to_id= next_node_id,)

        return m

def main():
    st.set_page_config(layout="wide", page_title="Traffic Flow Analysis")
    st.title("Traffic Flow Analysis - Ho Chi Minh City")
    
    try:
        # Initialize app
        app = TrafficFlowUI()
        
        # Create two columns for the layout
        col1, col2 = st.columns([1, 3])
        
        # Control panel in first column
        with col1:
            st.header("Controls")
            
            # Location selection
            source = st.selectbox(
                "Source Location",
                options=list(app.node_name_lookup.keys()),
            )
            
            dest = st.selectbox(
                "Destination Location",
                options=[k for k in app.node_name_lookup.keys() if k != source],
            )
            
            # Algorithm selection
            algorithm = st.selectbox(
                "Algorithm",
                options=["Edmonds-Karp", "Dinic", "Ford-Fulkerson"]
            )
            
            calculate = st.button("Calculate Flow", use_container_width=True)
        
        # Main content area in second column
        with col2:
            if calculate:
                with st.spinner("Calculating maximum flow..."):
                    # Get source and sink indices in adjacency matrix 
                    source_node_id = app.node_name_lookup.get(source)
                    sink_node_id = app.node_name_lookup.get(dest)
                    source_idx = app.node_index_lookup.get(str(source_node_id))
                    sink_idx = app.node_index_lookup.get(str(sink_node_id))
                    
                    # Initialize algorithm
                    if algorithm == "Edmonds-Karp":
                        algo = Edmond_Karps(app.adj_matrix)
                    elif algorithm == "Ford-Fulkerson":
                        algo = FordFulkerson(app.adj_matrix)
                    else:
                        algo = Dinic(app.adj_matrix)
                    
                    # Run selected algorithm
                    start = time.time()
                    flow = algo.execute(source=source_idx, sink=sink_idx)
                    end = time.time()
                    run_time = end - start
                    paths = algo.paths
                    
                    # Store results
                    st.session_state.flow_results = {
                        'flow': flow,
                        'time': run_time,
                        'paths': paths
                    }
            
            # Display results if available
            if 'flow_results' in st.session_state and st.session_state.flow_results:
                results = st.session_state.flow_results
                
                # Display metrics
                metric_cols = st.columns(2)
                with metric_cols[0]:
                    st.metric("Maximum Flow", f"{results['flow']:.1f} vehicles/hour")
                with metric_cols[1]:
                    st.metric("Computation Time", f"{results['time']:.3f} seconds")
                
                # Display map
                st.subheader("Flow Visualization")
                m = app.create_basic_map(paths= results['paths'])
                st_folium(m, width=800)
                
                # Display paths
                if results['paths']:
                    st.subheader("Path Details")
                    for i, path_info in enumerate(results['paths']):
                        path = path_info['path']
                        flow = path_info['flow']
                        path_nodes = []
                        for node_idx in path:
                            node_id = app.index_node_lookup.get(node_idx)
                            node_name = app.node_id_to_name.get(node_id, str(node_id))
                            path_nodes.append(node_name)
                        # Create the formatted string
                        path_str = f"Path {i+1}: "
                        for j in range(len(path_nodes) - 1):
                            path_str += f"{path_nodes[j]} ----({flow})-----> "
                        path_str += f"{path_nodes[-1]}"
                        st.write(path_str)
                        st.write('\n')
            else:
                # Display initial map
                st.subheader("Current Network")
                m = app.create_basic_map()
                st_folium(m, width=800)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please ensure all required data files are present and properly formatted.")

if __name__ == "__main__":
    main()
