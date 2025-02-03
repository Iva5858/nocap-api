from veritas_fact_check_api import app

# This is the application object needed by gunicorn
application = app

if __name__ == "__main__":
    application.run() 