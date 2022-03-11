import argparse
import logging

import numpy as np
import requests
import json
import http.client

from urllib.parse import urlencode

class InvalidParameterValueException(Exception):
	def __init__(self, message):
		self._message = message


class Operator:
	def __init__(self, format):
		fields = format.split('/')
		self._numerator = int(fields[0])
		self._denominator = int(fields[1])
		self._column_name = fields[2]


class Column:
	def __init__(self, format):
		fields = format.split('/')
		if len(fields) != 4:
			raise InvalidParameterValueException(
				"Column format: column_index/delimiter/[field_start-field_end|field_index_1,field_index_2]")
		self._column = int(fields[0])
		self._delimiter = fields[1]
		self._column_names = fields[3].split(',')
		fields = fields[2].split(',')
		self._fields = []
		for f in fields:
			if '-' in f:
				flds = f.split('-')
				self._fields += [i for i in range(int(flds[0]), int(flds[1]) + 1)]
			else:
				self._fields.append(int(f))


class DataAnalyzer:
	def __init__(self, column_seperator='\t', field_separator=':'):
		self._column_seperator = column_seperator
		self._field_separator = field_separator

	def _extract(self, source_file, head, column):
		column = Column(column)
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

	def extract_columns(self, source_file, columns, head, output_file):
		data = [*self._extract(source_file, head, columns)]
		with open(output_file, 'w', newline='') as file:
			for i in range(0, len(data)):
				file.write('\t'.join(data[i]) + '\n')

	def merge_files(self, source_file, output_filename):
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
						column_names += '\t'*(len(line.split(self._column_seperator))-1)
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

	def _split(self, source_file, head, column):
		column = Column(column)
		with open(source_file, newline='') as file:
			column_names = []
			if head:
				column_names += file.readline().split(self._column_seperator)

			column_names = column_names[0: column._column] + column._column_names + column_names[column._column + 1:]
			yield np.array(column_names)

			while True:
				line = file.readline()
				if not line:
					break
				cols = line.rstrip('\n').split(self._column_seperator)
				try:
					fs = np.array(cols[column._column].split(column._delimiter))
					yield np.concatenate(
						(np.array(cols[0: column._column]), fs[column._fields], np.array(cols[column._column + 1:])),
						axis=0)
				except IndexError as err:
					logging.error(fs)

	def split_columns(self, source_file, columns, head, output_file):
		data = [*self._split(source_file, head, columns)]
		with open(output_file, 'w', newline='') as file:
			for i in range(0, len(data)):
				file.write('\t'.join(data[i]) + '\n')

	def _parse_operator(self, format):
		for d in format.split(','):
			yield (Operator(d))

	def divide(self, source_file, columns, head, output_file):
		operators = [*self._parse_operator(columns)]
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
		for divider in operators:
			column_names.append(divider._column_name)
		for row in data:
			for operator in operators:
				if float(row[operator._denominator]) > 0:
					row.append("{:.2f}".format(float(row[operator._numerator]) / float(row[operator._denominator])))

		with open(output_file, 'w', newline='') as file:
			file.write('\t'.join(column_names) + '\n')
			for i in range(0, len(data)):
				file.write('\t'.join(data[i]) + '\n')

	def add(self, source_file, columns, head, output_file):
		operators = [*self._parse_operator(columns)]
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

	def search_by_gene_name(self, input_filename, column_index, gene_names, column_delimiter, gene_delimiter, head, output_filename):
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
				headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8","Accept": "text/plain"}
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
					head_line.insert(column_index+1, "gene.name")
					output_file.write(",".join(head_line))

				while True:
					line = input_file.readline()
					if not line:
						break
					cols = line.split(column_delimiter)
					cols.insert(column_index+1, map[cols[column_index].strip('"')])
					output_file.write(",".join(cols))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Calculate the ratio of column 6 over column 2. ")
	parser.add_argument('--action',
						help="what action will be performed, valid values are extract, split, merge, calculate_ratio",
						action='store', dest='action')
	parser.add_argument('--source_file', help="A source file delimited by tab ", action='store', dest='source_file')
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

	head = True if args.head == 'True' else False
	if args.action == 'strip':
		data_analyzer.strip(args.source_file, int(args.column_index), head, args.column_delimiter, int(args.field_index), args.field_delimiter, args.output_file)
	elif args.action == 'prefix':
		data_analyzer.prefix(args.source_file, args.prefix, int(args.column_index), head, args.column_delimiter,args.output_file)
	elif args.action == 'extract':
		data_analyzer.extract_columns(args.source_file, args.columns, head, args.output_file)
	elif args.action == 'split':
		data_analyzer.split_columns(args.source_file, args.columns, head, args.output_file)
	elif args.action == 'merge':
		data_analyzer.merge_files(args.source_file, args.output_file)
	elif args.action == 'add':
		data_analyzer.add(args.source_file, args.columns, head, args.output_file)
	elif args.action == 'divide':
		data_analyzer.divide(args.source_file, args.columns, head, args.output_file)
	elif args.action == 'search_by_gene_name':
		data_analyzer.search_by_gene_name(args.source_file,
										  int(args.columns.split(',')[0]),
										  args.gene_names,
										  args.column_delimiter,
										  args.gene_delimiter,
										  head,
										  args.output_file)
	elif args.action == 'get_gene_name':
		data_analyzer.get_gene_name_by_id(args.source_file, int(args.columns.split(',')[0]), args.column_delimiter,head, args.output_file)
	else:
		usage = """
			Here are actions supported right now:
				- extract
				- split
				- merge
				- add
				- divide"""

		logging.info(usage)
