# Map Flow Analysis Application

An application to analyze maximum flow in road networks based on OpenStreetMap data.

## File Structure

```
.
├── config/                  # Configuration files
│   └── key_locations.json  # Metadata for key locations
├── road_network_extractor.py  # Script to crawl map data from location centroids
├── maximum_flow_algorithms.py # Maximum flow implementation
└── streamlit_app.py          # User interface
```

The `road_network_extractor.py` download map data from api, including intersection locations (node) and road connecting locations (edge). Each road has an attributes on type of road (`highway`) and number of lanes. A capacity mapping based on type of road is predined, and the final estimate of `road capacity = road_capacity * number_of_lanes`. 

## Installation

### Prerequisites
- pip package manager
- bash shell environment

### Setup Instructions

1. Navigate to the Map directory:
```bash
cd Map
```

2. Create a Python virtual environment:
```bash
python3 -m venv .py-env
```

3. Activate the virtual environment:
```bash
source .py-env/bin/activate
```

4. Install required dependencies:
```bash
pip install requirements.txt
```

### Running the Application

1. Execute the application using the provided shell script:
```bash
bash map_app.sh
```

2. In case bash command does not work properly. Run below command in sequence 
```bash
python3 road_network_extractor.py
python3 maximum_flow_algorithms.py
streamlit run streamlit_app.py
```


## User Interface Guide

![Map Flow Analysis Demo](./map_demo.png)

### Usage Instructions

1. Use the left panel to:
   - Select your target location
   - Choose the flow algorithm
   - Click "Calculate Flow" to process

### Performance Note

If you experience performance issues due to large map datasets, you can adjust the map coverage by reducing the `MAP_RADIUS` parameter in `config.py`.

## Configuration

The application's behavior can be customized through the following settings in `config.py`:
- `MAP_RADIUS`: Controls the area of map data to process
- `KEY LOCATIONS`: List of key locations coordinates and representative name

