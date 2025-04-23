import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.retrieval_gen.rag import run_rag

answer = run_rag("In which year was ucc founded, who founded it and what are some of the courses you can take at ucc?")
print(answer["answer"])
for src in answer["context"]:
    print("•", src.metadata["url"])
