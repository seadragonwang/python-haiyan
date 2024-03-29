import argparse
import logging

import numpy as np
import requests
import json
import http.client

from urllib.parse import urlencode

from field import Field
from merged_column import MergedColumn
from splited_column import SplitedColumn


class DataAnalyzer:
  def __init__(self, column_seperator='\t', field_separator=':'):
    self._column_seperator = column_seperator
    self._field_separator = field_separator

  def intersect(self, source_file, source_file_2, head, column, output_file):
    column_indices = column.split('/')
    head_lines = head.split('/')
    filter_keys = set()
    with open(source_file, 'r') as fin:
      for i in range(0, int(head_lines[0])):
        fin.readline()
      line = fin.readline()
      while line:
        fields = line.split("\t")
        filter_keys.add(fields[int(column_indices[0])].strip())
        line = fin.readline()

    with open(output_file, 'w', newline='') as fout:
      with open(source_file_2, 'r') as fin2:
        for i in range(0, int(head_lines[1])):
          fout.write(fin2.readline())
        line = fin2.readline()
        while line:
          key = line.split("\t")[int(column_indices[1])]
          if key in filter_keys:
            fout.write(line)
          line = fin2.readline()

  def extract(self, source_file, head, column):
    column = SplitedColumn(column)
    with open(source_file, 'r') as file:
      if head:
        file.readline()
      yield np.array(column._column_names)

      while True:
        line = file.readline()
        if not line:
          break
        cols = line.split(self._column_seperator)
        try:
          fs = np.array(cols[column._column].split(column._delimiter))
          yield fs[column._fields]
        except IndexError as err:
          logging.error(fs)

  def strip(self, source_file, column_index, head, column_delimiter, field_index, field_delimiter, output_file):
    with open(output_file, 'w', newline='') as output_file:
      with open(source_file, 'r') as input_file:
        while True:
          line = input_file.readline()
          if not line:
            break
          if head:
            output_file.write(line)
          else:
            cols = line.split(column_delimiter)
            fields = cols[column_index].split(field_delimiter)
            fields.remove(fields[field_index])
            cols[column_index] = field_delimiter.join(fields)
            output_file.write(column_delimiter.join(cols))

  def prefix(self, source_file, prefix, column_index, head, column_delimiter, output_file):
    with open(output_file, 'w', newline='') as output_file:
      with open(source_file, 'r') as input_file:
        while True:
          line = input_file.readline()
          if not line:
            break
          if head:
            output_file.write(line)
          else:
            cols = line.split(column_delimiter)
            cols[column_index] = prefix + cols[column_index]
            output_file.write(column_delimiter.join(cols))

  # def extract_columns(self, source_file, columns, head, output_file):
  # 	with open(output_file, 'w', newline='') as file:
  # 		with open(source_file, 'r') as input:
  # 		for i in range(0, len(data)):
  # 			file.write('\t'.join(data[i]) + '\n')

  def select_columns(self, source_file, columns, head, output_file):
    column_items = list([x.split(":") for x in columns.split(",")])
    with open(output_file, 'w', newline='') as file:
      with open(source_file, 'r') as input:
        if eval(head):
          line = input.readline()
        column_names = list([x[1] for x in column_items])
        column_indices = list([int(x[0]) for x in column_items])
        file.write("\t".join(column_names) + "\n")
        while True:
          line = input.readline()
          if not line:
            break
          fields = line.strip("\n").split(self._column_seperator)
          file.write("\t".join(list([fields[i] for i in column_indices])))
          file.write("\n")

  def merge_files(self, source_file_1, source_file_2, output_filename):
    with open(output_filename, 'w', newline='') as output:
      s1fs = source_file_1.split(":")
      s2fs = source_file_2.split(":")
      with open(s1fs[0], 'r', newline='') as input_file_1:
        with open(s2fs[0], 'r', newline='') as input_file_2:
          line = ""
          line2 = ""
          if eval(s1fs[1]):
            line = input_file_1.readline().rstrip('\n').rstrip("\r")
          if eval(s2fs[1]):
            line2 = input_file_2.readline()
          output.write(line + self._column_seperator + line2)

          while True:
            line = input_file_1.readline()
            if not line:
              break
            output.write(line.rstrip('\n').rstrip("\r") + self._column_seperator + input_file_2.readline())

  def concatenate_files(self, source_file, output_filename):
    file_names = [f.split(':') for f in source_file.split(',')]
    data = []
    column_names = []
    for i in range(0, len(file_names)):
      head_added = False
      with open(file_names[i][0], 'r', newline='') as input_file:
        if file_names[i][1] == 'True':
          line = input_file.readline().rstrip('\n')
          column_names += line.split(self._column_seperator)
        index = 0
        while True:
          line = input_file.readline()
          if not line:
            break;
          if file_names[i][1] == 'False' and not head_added:
            column_names += '\t' * (len(line.split(self._column_seperator)) - 1)
            head_added = True
          if i < len(file_names) - 1:
            line = line.rstrip('\n')
          if i == 0:
            data.append(line)
          else:
            data[index] += self._column_seperator + line
            index += 1

    with open(output_filename, 'w') as output_file:
      output_file.write('\t'.join(column_names) + '\n')
      for row in data:
        output_file.write(row)

  def merge_columns(self, source_file, columns, head, output_file):
    fields = columns.split('/')
    merged_column = MergedColumn(columns)
    with open(output_file, 'w', newline='') as output:
      with open(source_file, newline='') as input:
        column_names = []
        if head:
          column_names += input.readline().strip("\n").split(self._column_seperator)

        column_names = column_names + merged_column._column_name
        output.write("\t".join(column_names) + "\n")
        while True:
          line = input.readline()
          if not line:
            break
          cols = line.rstrip('\n').split(self._column_seperator)
          new_col = ''
          for column_index in merged_column._source_columns:
            if new_col:
              new_col += merged_column._connector + cols[column_index]
            else:
              new_col = cols[column_index]
          cols.append(new_col)
          output.write(self._column_seperator.join(cols))

  def split_columns(self, source_file, columns, head, output_file):
    with open(output_file, 'w', newline='') as output:
      column = SplitedColumn(columns)
      with open(source_file, newline='') as file:
        column_names = []
        if eval(head):
          column_names += file.readline().split(self._column_seperator)
          column_names = column_names[0: column._column] + column._column_names + column_names[column._column + 1:]
          output.write("\t".join(column_names) + "\n")

        while True:
          line = file.readline()
          if not line:
            break
          cols = line.rstrip('\n').split(self._column_seperator)
          try:
            fs = cols[column._column].strip('"').strip("\r").split(column._delimiter)
            fs2 = list([fs[i] for i in column._fields])
            fs_final = []
            for f in fs2:
              if "," in f:
                fs3 = f.split(",")
                if len(fs3) == 3:
                  fs_final.append(str(int(fs3[0]) + int(fs3[1])))
                  fs_final.append(fs3[2])
                else:
                  fs_final.append(fs3[0])
                  fs_final.append(fs3[1])
              else:
                fs_final.append(f)
            output.write("\t".join(cols[0: column._column] + fs_final + cols[column._column + 1:]))
            output.write("\n")
          except IndexError as err:
            logging.error(fs)

  def parse(self, format):
    for d in format.split(','):
      yield (Field(d))

  def divide(self, source_file, columns, head, output_file):
    operators = [*self.parse(columns)]
    with open(output_file, 'w', newline='') as output:
      with open(source_file, newline='') as input:
        if eval(head):
          column_names = input.readline().rstrip('\n').strip("\r").split(self._column_seperator)
          for divider in operators:
            column_names.append(divider._column_name)
          output.write("\t".join(column_names) + "\n")
        while True:
          line = input.readline().strip("\n").strip("\r")
          if not line:
            break
          row = line.split(self._column_seperator)
          for operator in operators:
            try:
              if float(row[operator._denominator]) > 0:
                row.append("{:.2f}".format(float(row[operator._numerator]) / float(row[operator._denominator])))
            except:
              print(row)
              exit(2)

          output.write('\t'.join(row) + '\n')

  def add(self, source_file, columns, head, output_file):
    operators = [*self.parse(columns)]
    data = []

    with open(source_file, newline='') as file:
      column_names = None
      if head:
        column_names = file.readline().rstrip('\n').split(self._column_seperator)
      while True:
        line = file.readline()
        if not line:
          break
        data.append(line.rstrip('\n').split(self._column_seperator))
    for operator in operators:
      column_names.append(operator._column_name)
    for row in data:
      for operator in operators:
        row.append(str(int(row[operator._numerator]) + int(row[operator._denominator])))

    with open(output_file, 'w', newline='') as file:
      file.write('\t'.join(column_names) + '\n')
      for i in range(0, len(data)):
        file.write('\t'.join(data[i]) + '\n')

  def search_by_gene_name(self, input_filename, column_index, gene_names, column_delimiter, gene_delimiter, head,
                          output_filename):
    gene_set = set(map(lambda s: s.lower().strip(), gene_names.split(',')))
    if column_delimiter == 'tab':
      column_delimiter = '\t'
    with open(output_filename, 'w', newline='') as output_file:
      with open(input_filename, newline='') as input_file:
        head_line = None
        if head:
          head_line = input_file.readline()
          output_file.write(head_line)
        while True:
          line = input_file.readline()
          if not line:
            break
          cols = line.split(column_delimiter)
          if cols[column_index]:
            genes = set(map(lambda s: s.lower(), cols[column_index].split(gene_delimiter)))
            if gene_set & genes:
              output_file.write(line)

  def get_gene_name_by_id(self, input_filename, column_index, column_delimiter, head, output_filename):
    with open(output_filename, 'w', newline='') as output_file:
      with open(input_filename, newline='') as input_file:
        head_line = None
        gene_ids = set()
        if head:
          input_file.readline()

        while True:
          line = input_file.readline()
          if not line:
            break
          cols = line.split(column_delimiter)
          gene_ids.add(cols[column_index].strip('"'))
        headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8", "Accept": "text/plain"}
        print(len(gene_ids))
        body = {
          "keep_ids": "on",
          "input_data": "\n".join(gene_ids)
        }
        conn = http.client.HTTPSConnection("www.biotools.fr")
        conn.request('POST', '/human/refseq_symbol_converter/?presenter=none', body=urlencode(body), headers=headers)
        response = conn.getresponse()
        # response = requests.post("https://www.biotools.fr/human/refseq_symbol_converter/?presenter=none", data=urlencode(body), headers=headers)
        if response.status == 200:
          genes = response.read().decode('ascii').split("\n")
          print(genes)
          map = {}
          for gene in genes:
            fields = gene.split('\t')
            if len(fields) == 2:
              map[fields[0]] = fields[1]
        input_file.seek(0)
        if head:
          head_line = input_file.readline().split(column_delimiter)
          head_line.insert(column_index + 1, "gene.name")
          output_file.write(",".join(head_line))

        while True:
          line = input_file.readline()
          if not line:
            break
          cols = line.split(column_delimiter)
          cols.insert(column_index + 1, map[cols[column_index].strip('"')])
          output_file.write(",".join(cols))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Calculate the ratio of column 6 over column 2. ")
  parser.add_argument('--action',
                      help="what action will be performed, valid values are extract, split, merge, calculate_ratio",
                      action='store', dest='action')
  parser.add_argument('--source_file', help="A source file delimited by tab ", action='store', dest='source_file')
  parser.add_argument('--source_file_2', help="A source file delimited by tab ", action='store', dest='source_file_2')
  parser.add_argument('--column_index', help="an index of column", action='store', dest='column_index')
  parser.add_argument('--field_index', help="an index of field", action='store', dest='field_index')
  parser.add_argument('--field_delimiter', help="field delimiter", action='store', dest='field_delimiter')
  parser.add_argument('--columns', help="pairs of columns", action='store', dest='columns')
  parser.add_argument('--prefix', help="prefix a string to a column", action='store', dest='prefix')
  parser.add_argument('--head', help="if there is a head row", action='store', dest='head')
  parser.add_argument('--column_delimiter', help="column delimiter", action='store', dest='column_delimiter')
  parser.add_argument('--gene_delimiter', help="gene delimiter", action='store', dest='gene_delimiter')
  parser.add_argument('--gene_names', help="gene name", action='store', dest='gene_names')
  parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

  args = parser.parse_args()
  data_analyzer = DataAnalyzer()

  if args.action == 'intersect':
    data_analyzer.intersect(args.source_file, args.source_file_2, args.head, args.columns, args.output_file)
  elif args.action == 'strip':
    data_analyzer.strip(args.source_file, int(args.column_index), args.head, args.column_delimiter,
                        int(args.field_index), args.field_delimiter, args.output_file)
  elif args.action == 'prefix':
    data_analyzer.prefix(args.source_file, args.prefix, int(args.column_index), args.head, args.column_delimiter,
                         args.output_file)
  elif args.action == 'select':
    data_analyzer.select_columns(args.source_file, args.columns, args.head, args.output_file)
  elif args.action == 'split':
    data_analyzer.split_columns(args.source_file, args.columns, args.head, args.output_file)
  elif args.action == 'merge':
    data_analyzer.merge_files(args.source_file, args.source_file_2, args.output_file)
  elif args.action == 'concatenate':
    data_analyzer.concatenate_files(args.source_file, args.output_file)
  elif args.action == 'add':
    data_analyzer.add(args.source_file, args.columns, args.head, args.output_file)
  elif args.action == 'divide':
    data_analyzer.divide(args.source_file, args.columns, args.head, args.output_file)
  elif args.action == 'search_by_gene_name':
    data_analyzer.search_by_gene_name(args.source_file,
                                      int(args.columns.split(',')[0]),
                                      args.gene_names,
                                      args.column_delimiter,
                                      args.gene_delimiter,
                                      args.head,
                                      args.output_file)
  elif args.action == 'get_gene_name':
    data_analyzer.get_gene_name_by_id(args.source_file, int(args.columns.split(',')[0]), args.column_delimiter,
                                      args.head, args.output_file)
  else:
    usage = """
			Here are actions supported right now:
				- intersect
				- strip
				- prefix
				- extract
				- split
				- merge
				- add
				- divide
				- search_by_gene_name
				- get_gene_name"""

    logging.info(usage)
