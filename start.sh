#!/bin/bash
gunicorn --bind 0.0.0.0:${PORT:-5555} app:app