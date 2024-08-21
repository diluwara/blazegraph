import requests

# Path to your TTL file
ttl_file_path = 'data.ttl'

# Blazegraph SPARQL endpoint for your namespace
namespace = 'myNamespace'  # Replace with your namespace
endpoint_url = f'http://localhost:9999/blazegraph/namespace/{namespace}/sparql'

# Read the TTL file
with open(ttl_file_path, 'r') as file:
    ttl_data = file.read()

# Headers for the request
headers = {
    'Content-Type': 'text/turtle'
}

# Send POST request to upload the TTL data
response = requests.post(endpoint_url, headers=headers, data=ttl_data)

# Check response status
if response.status_code == 200:
    print("Data uploaded successfully.")
else:
    print(f"Failed to upload data. Status code: {response.status_code}")
    print(response.text)
