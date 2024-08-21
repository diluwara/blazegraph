from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Function to create a namespace in Blazegraph
def create_blazegraph_namespace(namespace_name, mode='triples', inference=False, isolatable_indices=False,
                                text_index=False, geo_spatial=False):
    url = 'http://localhost:9999/blazegraph/#namespaces'  # Blazegraph instance URL
    
    headers = {
        'Content-Type': 'text/plain'
    }

    # Create the configuration for the namespace based on the options selected
    config = [
        f'com.bigdata.rdf.sail.namespace={namespace_name}',
        f'com.bigdata.rdf.sail.truthMaintenance={str(inference).lower()}',
        f'com.bigdata.rdf.store.AbstractTripleStore.textIndex={str(text_index).lower()}',
        'com.bigdata.rdf.store.AbstractTripleStore.justify=false',
        f'com.bigdata.namespace.{namespace_name}.spo.com.bigdata.btree.BTree.branchingFactor=1024',
        'com.bigdata.rdf.store.AbstractTripleStore.statementIdentifiers=false',
        'com.bigdata.rdf.store.AbstractTripleStore.axiomsClass=com.bigdata.rdf.axioms.NoAxioms',
        f'com.bigdata.rdf.store.AbstractTripleStore.quads={str(mode == "quads").lower()}',
        f'com.bigdata.rdf.store.AbstractTripleStore.geoSpatial={str(geo_spatial).lower()}',
        'com.bigdata.journal.Journal.groupCommit=false',
        f'com.bigdata.rdf.sail.isolatableIndices={str(isolatable_indices).lower()}',
        f'com.bigdata.namespace.{namespace_name}.lex.com.bigdata.btree.BTree.branchingFactor=400'
    ]
    
    payload = "\n".join(config)
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return {'message': f'Namespace {namespace_name} created successfully'}, 200
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500


create_blazegraph_namespace("test1")