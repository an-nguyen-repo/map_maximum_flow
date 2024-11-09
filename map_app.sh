#!/bin/bash

echo "PULLING MAP DATA "
if python3 road_network_extractor.py; then
    echo "road_network_extractor.py completed successfully."
else
    echo "road_network_extractor.py failed."
    exit 1
fi

echo "TEST RUN MAXIMUM FLOW ALGORITHM"
if python3 maximum_flow_algorithms.py; then
    echo "maximum_flow_algorithms.py completed successfully."
else
    echo "maximum_flow_algorithms.py failed."
    exit 1
fi

# Run the Streamlit app
echo "Starting Streamlit app..."
if streamlit run streamlit_app.py; then
    echo "Streamlit app is running."
else
    echo "Failed to start Streamlit app."
    exit 1
fi
