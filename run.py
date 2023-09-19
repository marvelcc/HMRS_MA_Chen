import os
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))

file_list = []
for root, _, files in os.walk(script_dir):
    for file in files:
        if file == 'optimization.py':
            file_list.append(os.path.join(root, file))

for py_file in file_list:
    print(f"Executing {py_file}")
    subprocess.run(["python3", py_file], check=True)
