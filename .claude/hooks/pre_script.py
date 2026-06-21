import os 


file_path = os.path.join(os.path.dirname(__file__), 'pre_script.txt')

with open(file_path, 'a') as f:
    f.write('This is a pre script hook.\n')