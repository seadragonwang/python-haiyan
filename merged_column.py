from invalid_parameter_exception import InvalidParameterValueException


class MergedColumn:
	def __init__(self, format):
		fields = format.split('/')
		if len(fields) != 3:
			raise InvalidParameterValueException(
				"Column format: column_index_1, column_index_2/connector/column_name")

		self._source_columns = fields[0].split(',')
		self._connector = fields[1]
		self._column_name = fields[2]