import uvicorn
import os
from main import app

if __name__ == "__main__":
    os.system('pip install -r requirements.txt')
    uvicorn.run(app, port=8000)
