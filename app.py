from flask import Flask, request, jsonify
from db_model import db
from instance_manager import create_and_run_instance, get_all_instances, start_instance, stop_instance

app = Flask(__name__)

# Configuration for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:786786@localhost/blazegraph'
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
    # print(get_pid_by_port(8080),"pid geyying")
    return jsonify(result)

@app.route('/get_all_instances', methods=['GET'])
def get_all_instances_route():
    try:
        instances = get_all_instances()
        return jsonify(instances), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
