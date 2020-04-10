import csv
import argparse


def read(filename):
    result = {}
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in reader:
            result[row[0]] = row
    return result

def calculateRatio(source_file_1, source_file_2, columns, output_file):
    data = read(source_file_1)
    if source_file_2:
        data2 = read(source_file_2)
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for key in data.keys():
                if key in data2.keys():
                    row = []
                    for col in columns:
                        if '/' in col:
                            cols = col.split('/')
                            if cols[0] and cols[1]:
                                if float(data2[key][int(cols[1])]) == 0:
                                    row.append(float("inf"))
                                else:
                                    row.append(float(data[key][int(cols[0])]) / float(data2[key][int(cols[1])]))
                            elif cols[0]:
                                row.append(data[key][int(cols[0])])

                            elif cols[1]:
                                row.append(data2[key][int(cols[1])])

                        else:
                            row.append(data[key][int(col)])
                    writer.writerow(row)
    else:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for key in data.keys():
                row = []
                skip = False;
                for col in columns:
                    if '/' in col:
                        cols = col.split('/')
                        if cols[0] and cols[1]:
                            if float(data[key][int(cols[1])]) == 0:
                                skip = True;
                                break;
                            else:
                                row.append(float(data[key][int(cols[0])])/float(data[key][int(cols[1])]))
                        elif cols[0]:
                            row.append(data[key][int(cols[0])])

                        elif cols[1]:
                            row.append(data[key][int(cols[1])])

                    else:
                        row.append(data[key][int(col)])
                if skip:
                    continue;
                writer.writerow(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate the ratio of column 6 over column 2. ")
    parser.add_argument('--source_file_1', help="A source file delimited by tab ", action='store', dest='source_file_1')
    parser.add_argument('--source_file_2', help="a second source file", action='store', dest='source_file_2')
    parser.add_argument('--columns', help="pairs of columns", action='store', dest='columns')
    parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

    args = parser.parse_args()

    calculateRatio(args.source_file_1, args.source_file_2, args.columns.split(','), args.output_file)