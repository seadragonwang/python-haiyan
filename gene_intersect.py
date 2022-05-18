import argparse


def read(filename, columns, header=0):
    result = {}
    with open(filename, 'r') as f:
        line = None
        for i in range(0, header):
            line = f.readline().strip()
        if not columns:
            line = f.readline().strip()
            fields = line.strip().split("\t")
            r = []
            for i in range(1, len(columns)):
                r.append(fields[int(columns[i])])
            result[columns[0]] = r
            while line:
                fields = line.split("\t")
                r = []
                for i in range(1, len(columns)):
                    r.append(fields[int(columns[i])])
                result[columns[0]] = r
                line = f.readline().strip()
        else:
            line = f.readline().strip()
            fields = line.split("\t")
            while line:
                fields = line.split("\t")
                result[fields[0]] = fields[1:]
                line = f.readline().strip()
        return result


def intersect(source_file_1, source_file_2, columns, output_file):
    cols = columns.split('/')
    if "*" == cols[0]:
        data = read(source_file_1, None)
    else:
        data = read(source_file_1, cols[0].split(","))

    if "*" == cols[1]:
        data2 = read(source_file_2, columns, 2)
    else:
        data2 = read(source_file_2, cols[0].split(","), 2)

    with open(output_file, 'w') as fout:
        for key in data2.keys():
            if key in data.keys():
                fout.write(key + "\t" + "\t".join(data2[key]) + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Intersect 2 files based on gene name. ")
    parser.add_argument('--source_file_1', help="A source file delimited by tab ", action='store', dest='source_file_1')
    parser.add_argument('--source_file_2', help="a second source file", action='store', dest='source_file_2')
    parser.add_argument('--columns', help="a needed columns", action='store', dest='columns')
    parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

    args = parser.parse_args()

    intersect(args.source_file_1, args.source_file_2, args.columns, args.output_file)
