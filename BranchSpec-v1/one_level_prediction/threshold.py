import time
from subprocess import Popen, PIPE
import progressbar
from time import sleep
import difflib
import json
import re


class Threshold:
    def __init__(self, file_path):
        self.path = file_path
        self.results = list()

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

    def find_threshold(self, lower_limit, upper_limit, line_number, line_content, run_name, note=''):
        thresholds = range(lower_limit, upper_limit)
        count = 0
        start = time.time()
        for threshold in thresholds:
            self.change_threshold(line_number, line_content, threshold)
            process = Popen(['rm', run_name], stdout=PIPE, stderr=PIPE)
            process = Popen(['make', run_name], stdout=PIPE, stderr=PIPE)
            sleep(3)
            process = Popen(['taskset', '0x02', './' + run_name], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            # print(stdout)
            # print(stderr)
            decoded_output = self.decode_stdout(stdout)
            self.get_results_from_stdout(threshold, decoded_output)
            print('Run {} execution time: {} seconds'.format(count, round(time.time() - start, 2)))
            count += 1
            start = time.time()
        self.save_results_to_file(note + run_name + '_' + str(lower_limit) + '-' + str(upper_limit))


    def decode_stdout(self, stdout):
        stdout = stdout.decode('utf-8')
        lines = stdout.split('\n')
        return lines

    def get_results_from_stdout(self, threshold, decoded_output):
        result = {'threshold': threshold}
        for line in decoded_output:
            if 'Total bit sent:' in line:
                values = re.findall(r'\d+', line)
                if len(values) == 3:
                    result['bits_sent'] = values[0]
                    result['total_errors'] = values[1]
                    result['stdout_threshold'] = values[2]
                else:
                    return None
        print(result)
        self.results.append(result)

    def save_results_to_file(self, program_name):
        results = sorted(self.results, key=lambda d: d['total_errors'])
        results_string = list()
        for result in results:
            results_string.append(str(result))
        results_string = '\n'.join(results_string)
        with open('{}_results.txt'.format(program_name), 'w') as file:
            file.write(results_string)


def main():
    while True:
        try:
            file_name = input('Please enter the file name:\n')
            run_name = input('Please enter the compiled file name:\n')
            lower_limit = input('Please enter a lower bound (inclusive) for threshold values:\n')
            upper_limit = input('Please enter an upper bound (exclusive) for threshold values:\n')
            note = input('Add note to filename (press enter to skip):\n')
            lower_limit = int(lower_limit)
            upper_limit = int(upper_limit)
            break
        except:
            print('Invalid Inputs')
    print('Lower Limit: ', lower_limit)
    print('Upper Limit: ', upper_limit)
    print('--- Beginning Testing ---\n')
    thresh = Threshold(file_name)
    line = '  THRESHOLD = {}; // Setup the threshold latency properly \n'
    thresh.find_threshold(lower_limit, upper_limit, 36, line, run_name, note)


if __name__ == '__main__':
    main()
