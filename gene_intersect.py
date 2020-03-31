import csv
import argparse


def read(filename, columns):
    result = {}
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in reader:

            r = []
            for i in range(1, len(columns)):
                r.append(row[int(columns[i])])
            result[row[int(columns[0])]] = r
    return result


def intersect(source_file_1, source_file_2, columns, output_file):
    data = read(source_file_1, columns)
    data2 = read(source_file_2, columns)

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for key in data.keys():
            if key in data2.keys():
                writer.writerow([key] + data[key] + data2[key])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Intersect 2 files based on gene name. ")
    parser.add_argument('--source_file_1', help="A source file delimited by tab ", action='store', dest='source_file_1')
    parser.add_argument('--source_file_2', help="a second source file", action='store', dest='source_file_2')
    parser.add_argument('--columns', help="a needed columns", action='store', dest='columns')
    parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

    args = parser.parse_args()

    intersect(args.source_file_1, args.source_file_2, args.columns.split(','), args.output_file)
