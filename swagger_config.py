swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Ajali API",
        "description": "API for reporting and managing incidents.",
        "version": "1.0.0"
    },
    "host": "127.0.0.1:5555",  # optional: helps Swagger UI generate full URLs
    "basePath": "/",
    "schemes": ["http"],  # change to ["https"] in production
    "consumes": [
        "application/json",
        "multipart/form-data"
    ],
    "produces": [
        "application/json"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: **Bearer &lt;your_token&gt;**"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ],
    "responses": {
        "404": {
            "description": "Resource not found"
        },
        "500": {
            "description": "Internal server error"
        }
    },
    "tags": [
        {
            "name": "Auth",
            "description": "Endpoints for user authentication and profile access"
        },
        {
            "name": "Incidents",
            "description": "Endpoints for reporting, viewing, and updating incidents"
        },
        {
            "name": "Media",
            "description": "Endpoints for uploading files/media related to incidents"
        }
    ]
}


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}


