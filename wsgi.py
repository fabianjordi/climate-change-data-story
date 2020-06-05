"""Application entry point."""
from application import create_app
import os

# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app = create_app(os.getenv('FLASK_ENV') or 'default')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)