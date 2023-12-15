import os
import time
import requests
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Generate PEDIA scores via REST api')
    parser.add_argument('--case_input', default='data', dest='case_input',
                        help='Path to the directory containing the case encodings or the single file containing the gallery encodings.')
    parser.add_argument('--output_dir', default='', dest='output_dir',
                        help='Path to the directory for saving the results.')
    parser.add_argument('--url', default='localhost', dest='url',
                        help='URL to the api.')
    parser.add_argument('--port', default=9000, dest='port',
                        help='Port to the api.')
    return parser.parse_args()

def analyze_json(case_input, output_dir, api_endpoint):

    # Opening input JSON file
    f = open(case_input)

    # returns JSON object as a dictionary
    data = json.load(f)

    r = requests.post(url=api_endpoint, json=data)

    # extracting data in json format
    data = r.json()

    output_filename = os.path.join(output_dir, os.path.basename(case_input))
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    args = parse_args()

    # api-endpoint
    predict_URL = "http://{}:9000/pedia".format(args.url)

    start_time = time.time()

    single_file = False
    if os.path.isfile(args.case_input):
        single_file = True

    # single file
    if single_file:
        print("Start processing {} file.".format(1))
        analyze_json(args.case_input, args.output_dir, predict_URL)
        print("Finished (1/1): {}".format(args.case_input))
    else:
        input_files = os.listdir(args.case_input)
        print("Start processing {} file.".format(len(input_files)))
        count = 1
        for input_file in input_files:
            filename = os.path.join(args.case_input, input_file)
            analyze_json(filename, args.output_dir, predict_URL)
            print("Finished ({}/{}): {}".format(count, len(input_files), filename))
            count += 1

    output_finished_time = time.time()
    print('Total running time: {:.2f}s'.format(output_finished_time - start_time))
    print('Output json files are saved in: {}'.format(args.output_dir))


if __name__ == '__main__':
    main()	
