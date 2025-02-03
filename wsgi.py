import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from veritas_fact_check_api import app

# This is the application object needed by gunicorn
application = app

# Configure the application
application.config['PROPAGATE_EXCEPTIONS'] = True
application.config['DEBUG'] = False

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    application.run(host='0.0.0.0', port=port) 