import requests
import xml.etree.ElementTree as ET

def create_namespace(namespace_name: str, url: str) -> tuple:
    """
    Creates a namespace in Blazegraph by sending a POST request with the appropriate configuration.

    Args:
        namespace_name (str): The name of the namespace to create.
        url (str): The endpoint URL for creating the namespace.

    Returns:
        tuple: A tuple containing the response status code and response text.
    """
    try:
        # Read the XML template
        with open('blazegraph_namespace_config.xml', 'r') as file:
            xml_template = file.read()
        
        # Replace the placeholder with the actual namespace name
        xml_data = xml_template.replace('{{namespace_name}}', namespace_name)
        
        # Set the headers for the request
        headers = {
            'Content-Type': 'application/xml'
        }
        
        # Send the POST request with the modified XML data
        response = requests.post(url, headers=headers, data=xml_data)
        
        # Return the response status code and text
        return response.status_code, response.text
    
    except FileNotFoundError:
        return 500, "Configuration file 'blazegraph_namespace_config.xml' not found."
    
    except requests.exceptions.RequestException as e:
        return 500, f"HTTP request failed: {str(e)}"
    
    except Exception as e:
        return 500, f"An unexpected error occurred: {str(e)}"


def extract_namespace_names(xml_response: str):
    # Parse the XML response
    root = ET.fromstring(xml_response)

    # Define the namespaces used in the XML (to handle prefixed tags)
    namespaces = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'dc': 'http://purl.org/dc/terms/',
        'void': 'http://rdfs.org/ns/void#',
        'kb': 'http://www.bigdata.com/rdf#/features/KB/'
    }

    # Extract and return the namespace names
    namespace_names = []
    for description in root.findall('rdf:Description', namespaces):
        namespace_element = description.find('kb:Namespace', namespaces)
        if namespace_element is not None:
            namespace_names.append(namespace_element.text)

    return namespace_names

