import csv
import argparse


def deduplicate(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        genes = set()
        for row in reader:
            if row[3] not in genes:
                genes.add(row[3])
                yield row


def process(source_file, output_file):
    data = [*deduplicate(source_file)]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        i = 0
        while i < len(data):
            writer.writerow(data[i])
            i = i + 1
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Deduplicate rows based on 4th column, which is gene name, file should be tab delimited. ")
    parser.add_argument('--source_file', help="A source file delimited by tab with the value 4th column is gene name", action='store', dest='source_file')
    parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

    args = parser.parse_args()

    process(args.source_file, args.output_file)