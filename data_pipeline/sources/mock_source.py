import json
import os

def fetch_data():
    """
    Fetches attraction data from the local mock JSON file.
    """
    # Construct a path relative to this script's location
    # This makes it robust to where the main pipeline script is run from
    script_dir = os.path.dirname(__file__)
    data_path = os.path.join(script_dir, '..', 'data', 'mock_attractions.json')

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} records from mock_attractions.json")
        return data
    except FileNotFoundError:
        print(f"Error: Mock data file not found at {data_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {data_path}")
        return []
