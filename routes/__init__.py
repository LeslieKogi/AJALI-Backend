# routes/__init__.py
from flask import Blueprint
from .auth import auth_bp
from .incidents import incidents_bp

__all__ = ['auth_bp', 'incidents_bp']