from invalid_parameter_exception import InvalidParameterValueException


class SplitedColumn:
  def __init__(self, format):
    fields = format.split('/')
    if len(fields) != 4:
      raise InvalidParameterValueException(
        "Column format: column_index/delimiter/[field_start-field_end|field_index_1,field_index_2]/column_name_1, column_name_2")
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
