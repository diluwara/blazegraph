import os
from flask import Flask, request, jsonify
import requests
from blazegraph_namespace import create_namespace
from db_model import db
from instance_manager import create_and_run_instance, get_all_instances, start_instance, stop_instance
from utils import get_instance_by_id

app = Flask(__name__)

# Configuration for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure that the tables are created within the application context
with app.app_context():
    db.create_all()


@app.route('/create_instance', methods=['POST'])
def create_instance_route():
    data = request.get_json()
    
    instance_name = data.get('instance_name')
    port = data.get('port')
    install_path = data.get('install_path')
    min_memory = data.get('min_memory')
    max_memory = data.get('max_memory')
    ip_address = data.get('ip_address', 'localhost')  # Default to 'localhost' if not provided
    
    if not instance_name or not port or not install_path:
        return jsonify({"error": "instance_name, port, and install_path are required"}), 400
    
    try:
        result = create_and_run_instance(instance_name, port, install_path, min_memory, max_memory, ip_address)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stop_instance', methods=['POST'])
def stop_instance_route():
    data = request.get_json()
    instance_id = data.get('id')   
    if not instance_id:
        return jsonify({"error": "Instance ID is required"}), 400  
    result = stop_instance(instance_id)
    return jsonify(result)

@app.route('/start_instance', methods=['POST'])
def start_instance_route():
    data = request.get_json()
    instance_id = data.get('id') 
    if not instance_id:
        return jsonify({"error": "Instance ID is required"}), 400
    result = start_instance(instance_id)
    return jsonify(result)

@app.route('/get_all_instances', methods=['GET'])
def get_all_instances_route():
    try:
        instances = get_all_instances()
        return jsonify(instances), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_instance/<int:instance_id>', methods=['GET'])
def get_instance_route(instance_id):
    try:
        # Call the function to get the instance by ID
        instance = get_instance_by_id(instance_id)
        if instance:
            # Prepare the instance data to return
            instance_data = {
                "id": instance.id,
                "instance_name": instance.instance_name,
                "port": instance.port,
                "ip_address": instance.ip_address,
                "status": instance.status,
                "pid": instance.pid,
                "folder": instance.folder,
                "min_memory": instance.min_memory,
                "max_memory": instance.max_memory
            }
            return jsonify(instance_data), 200
        else:
            return jsonify({"error": "Instance not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/create_namespace', methods=['POST'])
def create_namespace_route():
    data = request.get_json()
    instance_id = data.get('id')
    namespace_name = data.get('namespace_name')  # Allow the client to specify the namespace name

    if not instance_id:
        return jsonify({"error": "Instance ID is required"}), 400

    if not namespace_name:
        return jsonify({"error": "Namespace name is required"}), 400

    instance = get_instance_by_id(instance_id)
    if instance:
        # Construct the namespace URL
        namespace_url = f"http://{instance.ip_address}:{instance.port}/blazegraph/namespace"

        # Create the namespace using the `create_namespace` function
        status_code, response_text = create_namespace(namespace_name, url=namespace_url)

        if status_code in [200, 201]:
            return jsonify({"message": "Namespace created successfully", "namespace_name": namespace_name}), status_code
        else:
            return jsonify({"error": "Failed to create namespace", "details": response_text}), status_code
    else:
        return jsonify({"error": "Instance not found"}), 404
    


@app.route('/upload_ttl', methods=['POST'])
def upload_ttl_route():
    instance_id = request.form.get('id')
    namespace_name = request.form.get('namespace_name')
    ttl_file = request.files.get('ttl_file')  # 'ttl_file' is the field name for the file

    if not instance_id:
        return jsonify({"error": "Instance ID is required"}), 400

    if not namespace_name:
        return jsonify({"error": "Namespace name is required"}), 400

    if not ttl_file:
        return jsonify({"error": "TTL file is required"}), 400

    # Retrieve instance information (assume get_instance_by_id is defined elsewhere)
    instance = get_instance_by_id(instance_id)
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    namespace_url = f"http://{instance.ip_address}:{instance.port}/blazegraph/namespace/{namespace_name}/sparql"

    # Read the contents of the uploaded file
    ttl_data = ttl_file.read().decode('utf-8')

    headers = {
        'Content-Type': 'text/turtle'
    }

    response = requests.post(namespace_url, headers=headers, data=ttl_data)

    if response.status_code == 200:
        return jsonify({"message": "Data uploaded successfully."}), 200
    else:
        return jsonify({
            "error": "Failed to upload data",
            "status_code": response.status_code,
            "response": response.text
        }), response.status_code

from flask import request, jsonify


@app.route('/run_query', methods=['POST'])
def run_query_route():
    data = request.get_json()
    instance_id = data.get('id')
    namespace_name = data.get('namespace_name')
    query = data.get('query')  # Query is now sent as part of the JSON payload

    if not instance_id:
        return jsonify({"error": "Instance ID is required"}), 400

    if not namespace_name:
        return jsonify({"error": "Namespace name is required"}), 400

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Retrieve instance information (assume get_instance_by_id is defined elsewhere)
    instance = get_instance_by_id(instance_id)
    if not instance:
        return jsonify({"error": "Instance not found"}), 404

    namespace_url = f"http://{instance.ip_address}:{instance.port}/blazegraph/namespace/{namespace_name}/sparql"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Send the query to Blazegraph
    response = requests.post(namespace_url, headers=headers, data={'query': query})

    if response.status_code == 200:
        try:
            # Try to parse the response as JSON
            result = response.json()
        except ValueError:
            # If parsing fails, return the raw text
            result = response.text
        return jsonify({"result": result}), 200
    else:
        return jsonify({
            "error": "Failed to run query",
            "status_code": response.status_code,
            "response": response.text
        }), response.status_code
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
