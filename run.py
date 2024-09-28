from src.app import app
from waitress import serve

serve(app, listen='0.0.0.0:8080', url_scheme='https')