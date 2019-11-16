import os
from datetime import datetime

class Record:
    
    def __init__(self, path):
        self.path = self.create_folder(path)
        self.log_path = self.path + "/log.txt"
        open(self.log_path, 'w').close()
        
    def create_folder(self, path):
        now = datetime.now()
        current_date = now.strftime("%y%m%d")
        path += current_date
        
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        
        return path
    
    def write_log(self, line):
        with open(self.log_path, "a") as file:
            file.write(line + "\n")
