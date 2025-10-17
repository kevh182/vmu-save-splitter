from datetime import datetime

class FileLog:
    def __init__(self):
        formatted_time = datetime.now().strftime("%Y%m%d%H%M%S")
        self.file_name = f"./file_log_{formatted_time}.txt"
        self.log_file = None

    def create_file_if_not_exists(self):
        if (not self.log_file):
            self.log_file = open(self.file_name, "w")

    def write_line(self, line: str):
        self.create_file_if_not_exists()
        self.log_file.write(f'{line}\n')