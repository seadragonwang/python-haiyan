import csv
import argparse


def read(filename):
    result = {}
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in reader:
           result[row[0]] = (row[1], row[5], float(row[5])/float(row[1]))
    return result

def calculateRatio(source_file_1, source_file_2, output_file):
    data = read(source_file_1)
    data2 = read(source_file_2)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        i = 0
        for key in data.keys():
            if data2[key][2] == 0:
                continue;
            if key in data2.keys():
                writer.writerow([key, data[key][0], data[key][1], data[key][2], data2[key][0], data2[key][1], data2[key][2], data[key][2]/data2[key][2]])
            i = i + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate the ratio of column 6 over column 2. ")
    parser.add_argument('--source_file_1', help="A source file delimited by tab ", action='store', dest='source_file_1')
    parser.add_argument('--source_file_2', help="a second source file", action='store', dest='source_file_2')
    parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

    args = parser.parse_args()

    calculateRatio(args.source_file_1, args.source_file_2, args.output_file)