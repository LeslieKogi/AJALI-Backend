from flask import Flask, request, jsonify
from flasgger import Swagger


import os
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

cloudinary.config( 
    cloud_name = "ddmykppxn", 
    api_key = "936797567636992", 
   api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)



app = Flask(__name__)

# Dummy in-memory "database"
incidents = {}
next_id = 1

@app.route('/')
def home():
    return "🚀 API is running! Visit /apidocs for Swagger UI."

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  
            "model_filter": lambda tag: True,  
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app, config=swagger_config)


@app.route('/incidents', methods=['POST'])
def create_incident():
    """
    Create a new incident
    ---
    tags:
      - Incidents
    parameters:
      - name: body
        in: body
        required: true
        schema:
          required:
            - title
            - description
          properties:
            title:
              type: string
              example: Accident on A104
            description:
              type: string
              example: A minor traffic collision near town
    responses:
      201:
        description: Incident created
    """
    global next_id
    data = request.get_json()
    incident = {
        "id": next_id,
        "title": data.get("title"),
        "description": data.get("description")
    }
    incidents[next_id] = incident
    next_id += 1
    return jsonify(incident), 201


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to Cloudinary
    ---
    tags:
      - Media
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Image file to upload
    responses:
      200:
        description: Upload successful
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file_to_upload = request.files['file']
    
    try:
        result = cloudinary.uploader.upload(file_to_upload)

        return jsonify({
            "message": "Upload successful",
            "secure_url": result["secure_url"],
            "public_id": result["public_id"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/incidents/<int:id>', methods=['PUT'])
def update_incident(id):
    """
    Update an incident
    ---
    tags:
      - Incidents
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Incident ID
      - name: body
        in: body
        required: true
        schema:
          properties:
            title:
              type: string
            description:
              type: string
    responses:
      200:
        description: Incident updated
      404:
        description: Incident not found
    """
    if id not in incidents:
        return jsonify({"error": "Incident not found"}), 404

    data = request.get_json()
    incidents[id]["title"] = data.get("title", incidents[id]["title"])
    incidents[id]["description"] = data.get("description", incidents[id]["description"])
    return jsonify(incidents[id]), 200


@app.route('/incidents/<int:id>', methods=['DELETE'])
def delete_incident(id):
    """
    Delete an incident
    ---
    tags:
      - Incidents
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Incident ID
    responses:
      200:
        description: Incident deleted
      404:
        description: Incident not found
    """
    if id not in incidents:
        return jsonify({"error": "Incident not found"}), 404

    del incidents[id]
    return jsonify({"message": f"Incident {id} deleted"}), 200


if __name__ == '__main__':
    app.run(debug=True)