#!/bin/bash

# Ensure the environment is set up
source /app/.venv/bin/activate

# Generate the schema diagram
python manage.py graph_models -a -o /app/myapp_models.png

# Deactivate the virtual environment
deactivate
