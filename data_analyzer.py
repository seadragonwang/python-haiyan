import argparse
import logging

import numpy as np


class InvalidParameterValueException(Exception):
	def __init__(self, message):
		self._message = message


class Divider:
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
				cols = line.split(self._column_seperator)
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
				file.write('\t'.join(data[i]))

	def _parse_divider(self, format):
		for d in format.split(','):
			yield (Divider(d))

	def calculate_ratio(self, source_file, columns, head, output_file):
		dividers = [*self._parse_divider(columns)]
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
		for divider in dividers:
			column_names.append(divider._column_name)
		for row in data:
			for divider in dividers:
				row.append("{:.2f}".format(float(row[divider._numerator]) / float(row[divider._denominator])))

		with open(output_file, 'w', newline='') as file:
			file.write('\t'.join(column_names) + '\n')
			for i in range(0, len(data)):
				file.write('\t'.join(data[i]) + '\n')


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Calculate the ratio of column 6 over column 2. ")
	parser.add_argument('--action',
						help="what action will be performed, valid values are extract, split, merge, calculate_ratio",
						action='store', dest='action')
	parser.add_argument('--source_file', help="A source file delimited by tab ", action='store', dest='source_file')
	parser.add_argument('--columns', help="pairs of columns", action='store', dest='columns')
	parser.add_argument('--head', help="if there is a head row", action='store', dest='head')
	parser.add_argument('--output_file', help='The output file', action='store', dest='output_file')

	args = parser.parse_args()
	data_analyzer = DataAnalyzer()

	head = True if args.head == 'True' else False
	if args.action == 'extract':
		data_analyzer.extract_columns(args.source_file, args.columns, head, args.output_file)
	elif args.action == 'split':
		data_analyzer.split_columns(args.source_file, args.columns, head, args.output_file)
	elif args.action == 'merge':
		data_analyzer.merge_files(args.source_file, args.output_file)
	elif args.action == 'calculate_ratio':
		data_analyzer.calculate_ratio(args.source_file, args.columns, head, args.output_file)
	else:
		usage = """
			Here are actions supported right now:
				- extract
				- split
				- merge
				- calculate_ratio"""

		logging.info(usage)
