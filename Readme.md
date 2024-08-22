## Environment Configuration

This application uses environment variables to manage sensitive information and configuration details. These variables are loaded from a `.env` file. For convenience, a `.env.example` file is provided in the repository to help you set up your environment.

### `.env.example` File

```env
# PostgreSQL Database URL
DATABASE_URL=postgresql://postgres:your_password@localhost/blazegraph
```

### Setting Up Your `.env` File

1. **Create a `.env` File**: Duplicate the `.env.example` file and rename it to `.env`.

2. **Update the Values**: Replace `your_password` with your actual PostgreSQL password in the `.env` file.

3. **Loading Environment Variables**: The application uses the `DATABASE_URL` environment variable to configure the database connection.

### Python Version

This application is built using **Python 3.10**. Ensure that you have Python 3.10 installed and available in your environment before running the application.

# Blazegraph Manager API

This API allows you to manage Blazegraph instances, namespaces, and upload TTL files or run SPARQL queries. It is built using Flask and connects to a PostgreSQL database to manage instance data.

## Configuration

- **Database:** PostgreSQL
- **Database URI:** `postgresql://postgres:password@localhost/dbname`
- **Flask Port:** `5000`

## Endpoints

### 1. **Create an Instance**

- **Endpoint:** `/create_instance`
- **Method:** `POST`
- **Description:** Creates and starts a new Blazegraph instance.
- **Request Body (JSON):**
  ```json
  {
    "instance_name": "my_instance",
    "port": 9999,
    "install_path": "/path/to/blazegraph",
    "min_memory": "512M",
    "max_memory": "1024M",
    "ip_address": "localhost"  // Optional, defaults to 'localhost'
  }
  ```
- **Response:**
  - `201 Created` with instance details on success.
  - `400 Bad Request` if required fields are missing.
  - `500 Internal Server Error` on failure.

### 2. **Stop an Instance**

- **Endpoint:** `/stop_instance`
- **Method:** `POST`
- **Description:** Stops a running Blazegraph instance.
- **Request Body (JSON):**
  ```json
  {
    "id": 1
  }
  ```
- **Response:**
  - `200 OK` with the result of the stop operation.
  - `400 Bad Request` if the instance ID is missing.
  - `500 Internal Server Error` on failure.

### 3. **Start an Instance**

- **Endpoint:** `/start_instance`
- **Method:** `POST`
- **Description:** Starts a stopped Blazegraph instance.
- **Request Body (JSON):**
  ```json
  {
    "id": 1
  }
  ```
- **Response:**
  - `200 OK` with the result of the start operation.
  - `400 Bad Request` if the instance ID is missing.
  - `500 Internal Server Error` on failure.

### 4. **Get All Instances**

- **Endpoint:** `/get_all_instances`
- **Method:** `GET`
- **Description:** Retrieves a list of all Blazegraph instances.
- **Response:**
  - `200 OK` with a list of instances.
  - `500 Internal Server Error` on failure.

### 5. **Get a Specific Instance**

- **Endpoint:** `/get_instance/<int:instance_id>`
- **Method:** `GET`
- **Description:** Retrieves details of a specific Blazegraph instance by ID.
- **Response:**
  - `200 OK` with instance details.
  - `404 Not Found` if the instance is not found.
  - `500 Internal Server Error` on failure.

### 6. **Create a Namespace**

- **Endpoint:** `/create_namespace`
- **Method:** `POST`
- **Description:** Creates a new namespace in a Blazegraph instance.
- **Request Body (JSON):**
  ```json
  {
    "id": 1,
    "namespace_name": "my_namespace"
  }
  ```
- **Response:**
  - `200 OK` or `201 Created` if the namespace is created successfully.
  - `400 Bad Request` if required fields are missing.
  - `404 Not Found` if the instance is not found.
  - `500 Internal Server Error` on failure.

### 7. **Upload TTL File**

- **Endpoint:** `/upload_ttl`
- **Method:** `POST`
- **Description:** Uploads a TTL (Turtle) file to a Blazegraph namespace.
- **Request Body (form-data):**
  - `id`: Instance ID
  - `namespace_name`: Name of the namespace
  - `ttl_file`: The TTL file to upload
- **Response:**
  - `200 OK` if the data is uploaded successfully.
  - `400 Bad Request` if required fields are missing.
  - `404 Not Found` if the instance is not found.
  - `500 Internal Server Error` on failure.

### 8. **Run a SPARQL Query**

- **Endpoint:** `/run_query`
- **Method:** `POST`
- **Description:** Runs a SPARQL query on a Blazegraph namespace.
- **Request Body (JSON):**
  ```json
  {
    "id": 1,
    "namespace_name": "my_namespace",
    "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 100"
  }
  ```
- **Response:**
  - `200 OK` with the query results.
  - `400 Bad Request` if required fields are missing.
  - `404 Not Found` if the instance is not found.
  - `500 Internal Server Error` on failure.

## Running the Application

To run the Flask application:

1. Install the necessary Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Flask server:
   ```bash
   python app.py
   ```

The server will start on `http://0.0.0.0:5000`.
