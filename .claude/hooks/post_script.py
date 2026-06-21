import os 


file_path = os.path.join(os.path.dirname(__file__), 'post_script.txt')

with open(file_path, 'a') as f:
    f.write('This is a post script hook.\n')