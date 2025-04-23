import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.utils.vectorize import ingest_docs

def main():
    print("Hello from ucc-info-chatbot!")

if __name__ == "__main__":
    ingest_docs()
