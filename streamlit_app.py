import streamlit as st
import folium
import numpy as np
from streamlit_folium import st_folium
import osmnx as ox
from maximum_flow_algorithms import Edmond_Karps, Dinic
from config import KEY_LOCATIONS
import pandas as pd 
import json 
import time 

class TrafficFlowUI:
    def __init__(self):
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load the network data"""
        try:
            # Load network data
            with open('./road_network_data.json', 'r') as file:
                data = json.load(file)

            self.adj_matrix = data['adjacent_matrix']
            self.node_name_lookup = data['node_name_lookup']
            self.node_index_lookup = data['node_index_lookup']
            self.nodes  = data['nodes']
            self.key_locations = data['key_locations']
            self.center_point = data['center_point']
            
            # Create simple node mapping
            #self.node_indices = {node: idx for idx, node in enumerate(self.nodes)}
            
            # # Load graph for visualization
            self.G = ox.load_graphml('road_network.graphml')
            
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            raise

    def create_basic_map(self, ):
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
        
        # Add paths if available
        points = []
        for node_id in self.nodes:
            node_data = self.G.nodes[node_id]
            latitude = node_data['lat']
            longitude = node_data['lon']
            points.append([latitude, longitude])

        folium.PolyLine(points, 
                color='#ba8e23',
                dash_array='5',
                weight = 1,
                opacity='.75',
                ).add_to(m)
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
                options=["Edmonds-Karp", "Dinic"]
            )
            
            calculate = st.button("Calculate Flow", use_container_width=True)
        
        # Main content area in second column
        with col2:
            if calculate:
                with st.spinner("Calculating maximum flow..."):
                    # Get source sink index in adjacent matrix 
                    source_idx = app.node_index_lookup.get(str(app.node_name_lookup.get(source)))
                    sink_idx = app.node_index_lookup.get(str(app.node_name_lookup.get(dest)))
                    print(source_idx, sink_idx)
                    # Initialize algorithm
                    edmonds = Edmond_Karps(app.adj_matrix)
                    dinic = Dinic(app.adj_matrix)
                    # Run selected algorithm
                    if algorithm == "Edmonds-Karp":
                        start = time.time()
                        flow = edmonds.execute(source= source_idx, sink= sink_idx)
                        end = time.time()
                        run_time = end - start 
                    else:
                        start = time.time()
                        flow = dinic.execute(source= source_idx, sink= sink_idx)
                        end = time.time()
                        run_time = end - start 
                    
                    # Store results
                    st.session_state.flow_results = {
                        'flow': flow,
                        'time': run_time,
                    }
            
            # Display results if available
            if 'flow_results' in st.session_state and st.session_state.flow_results:
                results = st.session_state.flow_results
                
                # Display metrics
                metric_cols = st.columns(3)
                with metric_cols[0]:
                    st.metric("Maximum Flow", f"{results['flow']:.1f} vehicles/hour")
                with metric_cols[1]:
                    st.metric("Computation Time", f"{results['time']:.3f} seconds")
                
                # Display map
                st.subheader("Flow Visualization")
                m = app.create_basic_map()
                st_folium(m, width=800)
                
                # # Display paths
                # if results['paths']:
                #     st.subheader("Path Details")
                #     for i, (path, flow) in enumerate(zip(results['paths'], results['flow_values'])):
                #         st.text(f"Path {i+1}: Flow = {flow:.1f} vehicles/hour")
            else:
                # Display initial map
                st.subheader("Current Network")
                m = app.create_basic_map()
                st_folium(m, width=800)
        
        # Add information about the application
        # st.sidebar.markdown("""
        # ### About
        # This application analyzes traffic flow between major points in Ho Chi Minh City
        # using maximum flow algorithms. The results show the theoretical maximum number
        # of vehicles that could travel between the selected points given the road network
        # capacity.
        # """)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please ensure all required data files are present and properly formatted.")

if __name__ == "__main__":
    main()