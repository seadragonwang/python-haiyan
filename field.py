class Field:
  def __init__(self, format):
    fields = format.split('/')
    self._numerator = int(fields[0])
    self._denominator = int(fields[1])
    self._column_name = fields[2]
