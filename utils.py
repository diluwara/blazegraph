import os
import shutil
import subprocess
from typing import Any, Dict, Literal, Tuple, Union
import psutil
import socket
import time

from db_model import Instance, db

def check_port_in_use(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False  # Port is not in use
        except socket.error:
            return True  # Port is in use

def wait_for_port(port, timeout=60):
    """Wait until the specified port is in use or timeout is reached."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port_in_use(port):
            return True
        time.sleep(1)
    return False
        

def get_pid(port):
    """Get the PID of the process using the specified port."""
    connections = psutil.net_connections()
    for con in connections:
        if con.raddr and con.raddr.port == port:
            return con.pid
        if con.laddr and con.laddr.port == port:
            return con.pid
    return -1

def end_pid(pid):
    """Terminate the process with the specified PID."""
    try:
        p = psutil.Process(pid)
        p.terminate()  # Or use p.kill() for a forceful termination
        return f"Process with PID {pid} has been terminated."
    except psutil.NoSuchProcess:
        return f"No process found with PID {pid}."
    except psutil.AccessDenied:
        return f"Access denied to terminate the process with PID {pid}."
    except Exception as e:
        return f"An error occurred: {e}"

def handle_existing_instance(instance_name: str, port: int) -> Tuple[Dict[str, str], Literal[400]]:
    """Handle case where an instance with the same name or port already exists."""
    return {"error": f"Instance {instance_name} already exists or port {port} is already in use"}, 400

def handle_running_instance(instance: Any) -> Tuple[Dict[str, str], Literal[400]]:
    """Handle the case where the instance is already running."""
    return {"error": f"Instance is already running with PID: {instance.pid}"}, 400

def start_process(command: str, instance_dir: str) -> subprocess.Popen:
    """Start the process for the instance."""
    return subprocess.Popen(command, cwd=instance_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def handle_failed_start(process: subprocess.Popen, error_message: str) -> Tuple[Dict[str, str], Literal[500]]:
    """Terminate the process and return an error message."""
    process.terminate()
    return {"error": error_message}, 500

# Helper function to retrieve an instance by ID
def get_instance_by_id(instance_id: Any) -> Instance:
    return Instance.query.filter_by(id=instance_id).first()

# Helper function to handle database commit and error
def commit_to_db(instance=None, process=None) -> Union[None, Tuple[Dict[str, str], Literal[500]]]:
    """Commit the current session to the database. If a process is provided, terminate it on failure."""
    if instance:
        db.session.add(instance)  # Add the instance to the session if provided
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Rollback the session to avoid partial commits
        if process:
            process.terminate()  # Terminate the process if commit fails
        return {"error": f"Failed to commit to the database: {str(e)}"}, 500
    return None

# Common function to create a directory for the new instance
def create_instance_directory(install_path: str, instance_name: str) -> str:
    base_dir = 'instances'  # Base directory where all instances will be stored
    instance_dir = os.path.join(base_dir, install_path, instance_name)
    os.makedirs(instance_dir, exist_ok=True)
    return instance_dir


# Common function to copy the JAR file
def copy_jar_file(instance_dir: str) -> None:
    shutil.copy('blazegraph.jar', instance_dir)

# Common function to set memory options and start the process
def prepare_and_start_process(instance_name: str, port: int, install_path: str, min_memory: str, max_memory: str, ip_address: str) -> subprocess.Popen:
    memory_opts = f"-Xms{min_memory} -Xmx{max_memory}" if min_memory and max_memory else ""
    command = f'java -server {memory_opts} -Djetty.port={port} -Djetty.host={ip_address} -jar blazegraph.jar'
    instance_dir = create_instance_directory(install_path, instance_name)
    copy_jar_file(instance_dir)
    return start_process(command, instance_dir)