import os
import json
from zephyr_api import ZephyrScaleAPI

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the config file
config_path = os.path.join(script_dir, '..', 'config', 'atlassian_config.yaml')

# Now you can use config_path to load the configuration
api = ZephyrScaleAPI(config_path=config_path)

print("Fetching latest 10 test cases from ESTS project...")
test_cases = api.get_ests_test_cases()

if test_cases:
    # Sort test cases by 'createdOn' in descending order to get the latest ones
    sorted_test_cases = sorted(test_cases, key=lambda x: x.get('createdOn', ''), reverse=True)

    print(f"Found {len(test_cases)} test cases in ESTS project. Displaying latest 10:")
    for i, tc in enumerate(sorted_test_cases[:10]): # Display only the first 10
        print(f"Test Case {i+1}: Key: {tc.get('key')}, Name: {tc.get('name')}, Status: {tc.get('status_name')}, Created On: {tc.get('created_date')}")
else:
    print("Could not retrieve test cases from ESTS project.")