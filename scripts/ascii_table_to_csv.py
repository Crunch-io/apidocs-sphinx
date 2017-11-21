#!/usr/bin/env python
"""
Convert reStructuredText tables to CSV format and back again.
This script does not handle tables with row or column spans.

Usage:
    ascii_table_to_csv.py [options] <input-filename> [<output-filename>]

Options:
    -i --input-format=FORMAT    [default: table:grid]
    -o --output-format=FORMAT   [default: csv]
    --test                      Run internal tests

Formats:
    csv
    table:grid
    table:simple

A filename of "-" means stdin/stdout. Default output-filename is "-".

See:
    http://docutils.sourceforge.net/docs/user/rst/quickref.html#tables
"""
from __future__ import print_function
import csv
import sys
import textwrap

import docopt


class Table(object):

    def __init__(self):
        self.headers = []  # one string per header
        self.rows = []  # [ (col1, col2, ..., coln), ... ]


class ReaderBase(object):

    def __init__(self, input_fileobj):
        self.input_fileobj = input_fileobj
        self.line_num = None

    def __call__(self):
        """
        Yield one Table object for each table found in the file.
        """
        # Each state method returns (next_state, table)
        state = self.start_state
        for line_num, line in enumerate(self.input_fileobj, 1):
            self.line_num = line_num
            state, table = state(line)
            if table is not None:
                yield table
        # Send EOF signal
        _, table = state('')
        if table is not None:
            yield table

    def error(self, msg):
        raise Exception("Error at {name}:{line}: {msg}"
              .format(
                name=self.input_fileobj.name,
                line=self.line_num,
                msg=msg))


class GridTableReader(ReaderBase):

    def __init__(self, input_fileobj):
        self.start_state = self.state_scanning_for_table
        super(GridTableReader, self).__init__(input_fileobj)
        self._reset()

    def _reset(self):
        self.table = None
        self.col_ranges = None  # [(start_index, end_index), ...]
        self.col_values = None  # [[line1, line2], ...]

    def _start_col_values(self):
        self.col_values = [[] for _ in self.col_ranges]

    def _accumulate_col_values(self, line):
        for i, range in enumerate(self.col_ranges):
            start_index, end_index = range
            self.col_values[i].append(line[start_index:end_index].strip())

    def _flush_col_values(self, dest_list):
        for col_value in self.col_values:
            dest_list.append(' '.join(cell_line for cell_line in col_value
                                      if cell_line))
        self._start_col_values()

    def state_scanning_for_table(self, line):
        if not line.startswith('+-'):
            return self.state_scanning_for_table, None
        assert self.table is None
        self.table = Table()
        assert self.col_ranges is None
        self.col_ranges = []
        prev_col_mark = -1
        for i in range(len(line)):
            if line[i] == '+':
                if prev_col_mark + 1 < i:
                    self.col_ranges.append((prev_col_mark + 1, i))
                prev_col_mark = i
        self._start_col_values()
        return self.state_scanning_headers, None

    def state_scanning_headers(self, line):
        if not line.strip():
            self.error("Premature end of header block")
        if line.startswith('+'):
            self._flush_col_values(self.table.headers)
            return self.state_scanning_body, None
        if not line.startswith('|'):
            self.error("Unexpected character at start of header line: {!r}"
                       .format(line[0]))
        self._accumulate_col_values(line)
        return self.state_scanning_headers, None

    def state_scanning_body(self, line):
        if not line.strip():
            self.error("Premature end of table body")
        if line.startswith('+'):
            self.table.rows.append([])
            self._flush_col_values(self.table.rows[-1])
            return self.state_looking_for_next_row_or_table_end, None
        if not line.startswith('|'):
            self.error("Unexpected character at start of row line: {!r}"
                       .format(line[0]))
        self._accumulate_col_values(line)
        return self.state_scanning_body, None

    def state_looking_for_next_row_or_table_end(self, line):
        if not line.strip():
            # Blank line or EOF means end of table
            table = self.table
            self._reset()
            return self.state_scanning_for_table, table
        if line.startswith('|'):
            return self.state_scanning_body(line)
        self.error("Unexpected character after table body end: {!r}"
                   .format(line[0]))


class CsvTableReader(object):

    def __init__(self, input_fileobj):
        self.input_fileobj = input_fileobj

    def __call__(self):
        table = Table()
        r = csv.reader(self.input_fileobj)
        num_cols = 0
        for i, row in enumerate(r):
            if i == 0:
                num_cols = len(row)
                table.headers = row
            else:
                if len(row) < num_cols:
                    row.extend(['' for i in range(len(row) - num_cols)])
                table.rows.append(row[:num_cols])
        yield table


class CsvTableWriter(object):

    def __init__(self, output_fileobj, table):
        self.output_fileobj = output_fileobj
        self.table = table

    def __call__(self):
        w = csv.writer(self.output_fileobj)
        w.writerow(self.table.headers)
        for row in self.table.rows:
            w.writerow(row)


def calc_line_length(col_widths):
    return sum(col_widths) + len(col_widths)


def calc_max_col_widths(table, never_wrap_first_col=True):
    def _calc_max_line_len(i, s):
        if never_wrap_first_col and i == 0:
            s = s.replace('\n', ' ')
        line_lengths = [len(line) for line in s.splitlines()]
        if not line_lengths:
            line_lengths = [0]
        return max(line_lengths)
    max_col_widths = [_calc_max_line_len(i, h) for i, h in
                      enumerate(table.headers)]
    for row in table.rows:
        for index, item in enumerate(row):
            n = _calc_max_line_len(index, item)
            if n > max_col_widths[index]:
                max_col_widths[index] = n
    return max_col_widths


def calc_min_col_widths(table, never_wrap_first_col=True):
    tw = textwrap.TextWrapper(
        width=1,
        replace_whitespace=False,
        break_long_words=False,
        break_on_hyphens=False,  # this would mess up code
    )
    def _calc_cell_min_width(i, cell_text):
        if never_wrap_first_col and i == 0:
            return len(cell_text)
        return max([len(line) for line in tw.wrap(cell_text)])
    min_col_widths = [_calc_cell_min_width(i, h) for i, h in
                      enumerate(table.headers)]
    for row in table.rows:
        for index, item in enumerate(row):
            n = _calc_cell_min_width(index, item)
            if n > min_col_widths[index]:
                min_col_widths[index] = n
    return min_col_widths


def calc_col_widths(table, output_width, never_wrap_first_col=True):
    max_col_widths = calc_max_col_widths(table, never_wrap_first_col)
    if calc_line_length(max_col_widths) <= output_width:
        # Cells are all narrow, no optimization/wrapping needed
        return max_col_widths
    min_col_widths = calc_min_col_widths(table, never_wrap_first_col)
    if calc_line_length(min_col_widths) > output_width:
        # Best-effort, even though output_width is exceeded
        return min_col_widths
    # Yes this is a wasteful algorithm, but we're assuming small tables
    col_widths = list(min_col_widths)
    if never_wrap_first_col and len(col_widths) > 1:
        start_index = 1
    else:
        start_index = 0
    while calc_line_length(col_widths) < output_width:
        for i in range(start_index, len(col_widths)):
            if col_widths[i] < max_col_widths[i]:
                col_widths[i] += 1
                if calc_line_length(col_widths) >= output_width:
                    break
    return col_widths


def test():
    col_widths = [3, 4, 5]
    assert calc_line_length(col_widths) == 15

    t1 = Table()
    t1.headers = ['blah', 'bloo', 'bleeeee']
    t1.rows = [
        ['x', 'y', 'z'],
        ['xx', 'yy', 'zz',],
    ]
    assert calc_min_col_widths(t1) == [4, 4, 7]
    assert calc_max_col_widths(t1) == [4, 4, 7]
    assert calc_col_widths(t1, 80) == [4, 4, 7]
    assert calc_col_widths(t1, 10) == [4, 4, 7]

    t2 = Table()
    t2.headers = ['name', 'Description']
    t2.rows = [
        ['blah', 'A description with\nan embedded newline'],
        ['blee bloo', 'A description'],
    ]
    assert calc_min_col_widths(t2) == [9, 11]
    assert calc_max_col_widths(t2) == [9, 19]
    assert calc_col_widths(t2, 10) == [9, 11]
    assert calc_col_widths(t2, 22) == [9, 11]
    assert calc_col_widths(t2, 23) == [9, 12]
    assert calc_col_widths(t2, 29) == [9, 18]
    assert calc_col_widths(t2, 30) == [9, 19]
    assert calc_col_widths(t2, 80) == [9, 19]
    assert calc_min_col_widths(t2, never_wrap_first_col=False) == [4, 11]
    assert calc_col_widths(t2, 10, never_wrap_first_col=False) == [4, 11]
    assert calc_col_widths(t2, 80, never_wrap_first_col=False) == [9, 19]


class SimpleTableWriter(object):

    def __init__(self, output_fileobj, table, output_width=80):
        self.output_fileobj = output_fileobj
        self.table = table
        self.output_width = output_width

    def __call__(self):
        col_widths = calc_col_widths(self.table, self.output_width,
                                     never_wrap_first_col=True)
        wrappers = [None]
        for width in col_widths[1:]:
            w = textwrap.TextWrapper(
                width=width,
                replace_whitespace=False,
                break_long_words=False,
                break_on_hyphens=False,
            )
            wrappers.append(w)
        self._write_column_markers(col_widths, '=')
        self._write_row(col_widths, wrappers, self.table.headers)
        for i, row in enumerate(self.table.rows):
            if i == 0:
                self._write_column_markers(col_widths, '=')
            else:
                self._write_column_markers(col_widths, '-')
            self._write_row(col_widths, wrappers, row)
        self._write_column_markers(col_widths, '=')

    def _write(self, s):
        self.output_fileobj.write(s)

    def _write_column_markers(self, col_widths, marker):
        for i, width in enumerate(col_widths):
            self._write(marker * width)
            if i == len(col_widths) - 1:
                self._write('\n')
            else:
                self._write(' ')

    def _write_row(self, col_widths, wrappers, row):
        assert len(col_widths) == len(wrappers)
        assert len(col_widths) == len(row)
        col_lines = []
        for i, row in enumerate(row):
            wrapper = wrappers[i]
            if wrapper is None:
                col_lines.append([row.replace('\n', ' ')])
            else:
                col_lines.append(wrapper.wrap(row))
        max_lines = max([len(lines) for lines in col_lines])
        for i in range(max_lines):
            for j, width in enumerate(col_widths):
                if i < len(col_lines[j]):
                    line = col_lines[j][i]
                else:
                    line = ''
                self._write(line)
                self._write(' ' * (width - len(line)))
                if j == len(col_widths) - 1:
                    self._write('\n')
                else:
                    self._write(' ')


READER_MAP = {
    'table:grid': GridTableReader,
    'csv': CsvTableReader,
}

WRITER_MAP = {
    'csv': CsvTableWriter,
    'table:simple': SimpleTableWriter,
}


def convert_table(input_fileobj, output_fileobj, input_format,
                  output_format):
    reader_class = READER_MAP.get(input_format)
    if reader_class is None:
        raise NotImplementedError("Unsupported input format: {}"
                                  .format(input_format))
    writer_class = WRITER_MAP.get(output_format)
    if writer_class is None:
        raise NotImplementedError("Unsupported output format: {}"
                                  .format(output_format))
    for table in reader_class(input_fileobj)():
        writer_class(output_fileobj, table)()
        # Only handle one table per input file
        break


def main():
    args = docopt.docopt(__doc__)
    if args['--test']:
        return test()
    input_filename = args['<input-filename>']
    output_filename = args['<output-filename>']
    if not output_filename:
        output_filename = '-'
    input_format = args['--input-format']
    output_format = args['--output-format']
    if input_filename == '-':
        input_fileobj = sys.stdin
    else:
        input_fileobj = open(input_filename)
    if output_filename == '-':
        output_fileobj = sys.stdout
    else:
        output_fileobj = open(output_filename, 'wb')
    try:
        convert_table(input_fileobj, output_fileobj, input_format,
                      output_format)
    finally:
        if output_filename != '-':
            output_fileobj.close()
        if input_filename != '-':
            input_fileobj.close()


if __name__ == '__main__':
    sys.exit(main())
