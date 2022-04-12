import os
from dotenv import load_dotenv
from app.main import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run()
