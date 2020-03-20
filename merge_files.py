import csv
import argparse


def extract(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        head = True
        for row in reader:
            if head:
                yield row[16].split(":")[2:6]
                yield row[17].split(":")[2:6]
                head = False
            else:
                yield row[17].split(":")[2:6]


def addAdditionalColumns(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')

        for row in reader:
            yield row



def process(source_file_1, source_file_2, output_file):
    data = [*extract(source_file_1)]
    data2 = [*addAdditionalColumns(source_file_2)]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        i = 0
        while i < len(data2):
            data2[i].append(data[i][0])
            data2[i].append(data[i][1])
            data2[i].append(data[i][2])
            data2[i].append(data[i][3])
            writer.writerow(data2[i])

            i = i + 1
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract 17th and 18th columns from tab seperated text source file, the value of 17th and 18th columns are colon seperated value, and 4th to 7th values are extracted as seperate column, 17th column is extracted only one time as column header, then append to 2nd source file as additional columns and save to output file. ")
    parser.add_argument('--source_file_1', help="A source file delimited by tab with the value 17th and 18th column are colon delimited, and 4th to 7th value will be extracted", action='store', dest='source_file_1')
    parser.add_argument('--source_file_2', help="a second source file, which should has the same number of rows as 1st source file", action='store', dest='source_file_2')
    parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

    args = parser.parse_args()

    process(args.source_file_1, args.source_file_2, args.output_file)