import os
import glob

dir_path = 'logs/'
txt_files = glob.glob(dir_path + '*.txt')
for file_path in txt_files:
    base_name = os.path.basename(file_path)
    if not base_name.startswith('experiment_A'):
        os.remove(file_path)