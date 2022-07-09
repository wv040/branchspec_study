from subprocess import Popen, PIPE
import progressbar
from time import sleep
import difflib
import json


class Threshold:
    def __init__(self, file_path):
        self.path = file_path

    def read_file_contents(self, path = None):
        data = None
        if path is not None:
            file_path = path
        else:
            file_path = self.path
        with open(file_path, 'r') as file:
            data = file.readlines()
        return data

    def write_file_contents(self, data, path=None):
        data = ''.join(data)
        if path is not None:
            file_path = path
        else:
            file_path = self.path
        with open(file_path, 'w') as file:
            file.write(data)

    def change_threshold(self, line_number, line, value):
        line_number = line_number - 1
        data = self.read_file_contents()
        data[line_number] = line.format(value)
        self.write_file_contents(data)

    def find_threshold(self, lower_limit, upper_limit, line_number, line_content, run_name):
        thresholds = range(lower_limit, upper_limit)
        work_units = upper_limit - lower_limit
        print('work_units:', work_units)
        bar = progressbar.ProgressBar(max_value=work_units)
        bar_count = 0
        for threshold in thresholds:
            self.change_threshold(line_number, line_content, threshold)
            process = Popen(['rm', run_name], stdout=PIPE, stderr=PIPE)
            process = Popen(['make', run_name], stdout=PIPE, stderr=PIPE)
            sleep(3)
            process = Popen(['taskset', '0x02', './' + run_name], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
            print(stderr)
            bar.update(bar_count)
            bar_count += 1


def main():
    thresh = Threshold('poc_v1.c')
    line = '  THRESHOLD = {}; // Setup the threshold latency properly \n'
    thresh.find_threshold(180, 182, 36, line, 'poc_v1')


if __name__ == '__main__':
    main()
