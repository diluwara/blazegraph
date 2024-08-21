import os
import psutil
import signal
from typing import Any, Dict, Tuple, Union, Literal
from utils import commit_to_db, get_instance_by_id, get_pid, handle_failed_start, handle_existing_instance, handle_running_instance, prepare_and_start_process, start_process, wait_for_port, check_port_in_use
from db_model import Instance


def create_and_run_instance(
    instance_name: str, port: int, install_path: str, min_memory: str, max_memory: str, ip_address: str, startup_timeout: int = 60
) -> Union[Dict[str, Any], Tuple[Dict[str, str], Literal[500]], Tuple[Dict[str, str], Literal[400]]]:
    
    # Check if an instance with the same name or port already exists
    if Instance.query.filter_by(instance_name=instance_name).first() or Instance.query.filter_by(port=port).first():
        return handle_existing_instance(instance_name, port)

    # Check if the port is in use by any process on the system
    if check_port_in_use(port):
        existing_pid = get_pid(port)
        return {"error": f"Port {port} is already in use by PID {existing_pid}"}, 400

    # Start the process
    process = prepare_and_start_process(instance_name, port, install_path, min_memory, max_memory, ip_address)

    # Wait for the process to bind to the port
    if not wait_for_port(port, timeout=startup_timeout):
        return handle_failed_start(process, f"Process did not bind to port {port} within {startup_timeout} seconds")
    
    # After the port is confirmed to be in use, retrieve the PID
    pid = get_pid(port)
    if pid == -1:
        return handle_failed_start(process, "Failed to retrieve PID after starting the process")

    # Create a new Instance record in the database
    new_instance = Instance(
        instance_name=instance_name,
        port=port,
        pid=pid,
        status='running',
        folder=os.path.join(install_path, instance_name),
        install_path=install_path,
        min_memory=min_memory,
        max_memory=max_memory,
        ip_address=ip_address
    )
    
    db_error = commit_to_db(new_instance, process)
    if db_error:
        return db_error

    return {"instance_name": instance_name, "port": port, "status": "running", "pid": pid}

def stop_instance(instance_id):
    instance = get_instance_by_id(instance_id)
    if instance and instance.status == 'running':
        try:
            # Check if the process is still running
            if psutil.pid_exists(instance.pid):
                os.kill(instance.pid, signal.SIGTERM)  # Kill the process
                instance.status = 'stopped'
                db_error = commit_to_db(instance)
                if db_error:
                    return db_error
                return {"instance_id": instance.id, "instance_name": instance.instance_name, "status": "stopped"}
            else:
                # Process is not running anymore
                instance.status = 'stopped'
                db_error = commit_to_db(instance)
                if db_error:
                    return db_error
                return {"instance_id": instance.id, "instance_name": instance.instance_name, "status": "already stopped"}
        except Exception as e:
            return {"error": str(e)}, 500
    return {"error": "Instance not found or already stopped"}, 404

def get_all_instances():
    instances = Instance.query.all()
    return [
        {
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
        for instance in instances
    ]

def get_instance_by_id(instance_id: Any) -> Instance:
    return Instance.query.filter_by(id=instance_id).first()

def start_instance(instance_id: Any) -> Union[Dict[str, Any], Tuple[Dict[str, str], Literal[500]], Tuple[Dict[str, str], Literal[400]], Tuple[Dict[str, str], Literal[404]]]:
    instance = get_instance_by_id(instance_id)
    if not instance:
        return {"error": "Instance not found or already running"}, 404

    if instance.status == 'stopped' or not psutil.pid_exists(instance.pid):
        process = prepare_and_start_process(instance.instance_name, instance.port, instance.install_path, instance.min_memory, instance.max_memory, instance.ip_address)

        if not wait_for_port(instance.port, timeout=60):
            return handle_failed_start(process, f"Process did not bind to port {instance.port} within the timeout period")

        pid = get_pid(instance.port)
        if pid == -1:
            return handle_failed_start(process, "Failed to retrieve PID after starting the process")
        
        instance.pid = pid
        instance.status = 'running'
        
        db_error = commit_to_db(instance, process)
        if db_error:
            return db_error

        return {
            "instance_id": instance.id,
            "instance_name": instance.instance_name,
            "ip_address": instance.ip_address,
            "port": instance.port,
            "status": "running",
            "pid": pid
        }
    
    if psutil.pid_exists(instance.pid):
        return handle_running_instance(instance)

    return {"error": "Instance not found or already running"}, 404
