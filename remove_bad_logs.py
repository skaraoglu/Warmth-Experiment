import os
import glob

# Define the directory
dir_path = '/logs/'

# Get list of all .txt files in the directory
txt_files = glob.glob(dir_path + '*.txt')

# Iterate over the list of filepaths & remove each file.
for file_path in txt_files:
    # Get the base name of the file (i.e., the file name without the directory info)
    base_name = os.path.basename(file_path)
    # If the file name doesn't start with 'A', remove it
    if not base_name.startswith('A'):
        os.remove(file_path)