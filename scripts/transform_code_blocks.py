#!/usr/bin/env python
"""
Transform consecutive ".. code::" blocks into ".. language_specific::"
blocks in reStructuredText.

Usage:
    transform_code_blocks.py [--inplace] <filename>...

Options:
    --inplace       Modify files in-place. Default is to write to stdout.

Unless --inplace is given, only the first filename is used.
"""
from __future__ import print_function
import shutil
import sys
import tempfile

import docopt


def get_line_indent(line):
    # Tabs counted as one indent character, oh well
    return len(line.rstrip()) - len(line.strip())


class CodeBlockTransformer(object):

    def __init__(self, in_fileobj, out_fileobj):
        self.in_fileobj = in_fileobj
        self.out_fileobj = out_fileobj
        self.buffered_line = None
        self.language = None
        self.code_lines = []
        self.starting_indent = None
        self.code_blocks = []  # [(language, code_lines), ...]

    def __call__(self):
        """Run the transformer"""
        state = self.state_looking_for_code_block
        while True:
            if self.buffered_line is not None:
                line = self.buffered_line
                self.buffered_line = None
            else:
                try:
                    line = next(self.in_fileobj)
                except StopIteration:
                    line = ''
                if not line:
                    self._flush_code_blocks()
                    break
            state = state(line)

    def state_looking_for_code_block(self, line):
        looking_for = '.. code::'
        if line.startswith(looking_for):
            assert self.language is None
            self.language = line[len(looking_for):].strip()
            return self.state_looking_for_non_blank_line
        self._flush_code_blocks()
        self.out_fileobj.write(line)
        return self.state_looking_for_code_block

    def state_looking_for_non_blank_line(self, line):
        if not line.strip():
            return self.state_looking_for_non_blank_line
        indent = get_line_indent(line)
        if indent == 0:
            # If we reach this point, we encountered an empty code block.
            # Throw away the info for the empty block and go back to
            # scanning for the next code block.
            self.buffered_line = line
            self.language = None
            self.code_lines = []
            return self.state_looking_for_code_block
        assert self.starting_indent is None
        self.starting_indent = indent
        assert not self.code_lines
        self.code_lines.append(line[self.starting_indent:])
        return self.state_scanning_code_block

    def state_scanning_code_block(self, line):
        indent = get_line_indent(line)
        if not line.strip() or indent >= self.starting_indent:
            self.code_lines.append(line[self.starting_indent:])
            return self.state_scanning_code_block
        self.starting_indent = None
        self.buffered_line = line
        # Trim trailing blank code lines
        while self.code_lines and not self.code_lines[-1].strip():
            self.code_lines.pop()
        # There should always be at least one code line
        assert self.code_lines
        self.code_blocks.append((self.language, self.code_lines))
        self.language = None
        self.code_lines = []
        return self.state_looking_for_code_block

    def _flush_code_blocks(self):
        if not self.code_blocks:
            return
        code_blocks = _coalesce_code_blocks(self.code_blocks)
        self.code_blocks = []
        def _writeln(s, indent=0):
            if s.strip():
                indent_str = ' ' * indent
            else:
                indent_str = ''
            self.out_fileobj.write("{}{}\n".format(indent_str, s))
        _writeln('.. language_specific::')
        for language, code_lines in code_blocks:
            if language in ('http', 'json'):
                display_language = language.upper()
            else:
                display_language = language.capitalize()
            _writeln('--{}'.format(display_language), indent=3)
            _writeln('.. code:: {}'.format(language), indent=3)
            _writeln('')
            for code_line in code_lines:
                _writeln(code_line.rstrip(), indent=6)
            _writeln('')
        _writeln('')


def _coalesce_code_blocks(code_blocks):
    """
    Combine consecutive code blocks with the same language, putting one
    blank line between them.
    """
    code_blocks_result = []
    prev_language = None
    for language, code_lines in code_blocks:
        if language != prev_language:
            prev_language = language
            code_blocks_result.append((language, list(code_lines)))
        else:
            # Blank line to separate from previous block of same language
            code_blocks_result[-1][1].append('\n')
            code_blocks_result[-1][1].extend(code_lines)
    return code_blocks_result


def main():
    args = docopt.docopt(__doc__)
    if args['--inplace']:
        for filename in args['<filename>']:
            print("Transforming", filename, "...")
            with tempfile.TemporaryFile() as out:
                with open(filename) as f:
                    CodeBlockTransformer(f, out)()
                out.seek(0)
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(out, f)
        print("Done.")
    else:
        filename = args['<filename>'][0]
        with open(filename) as f:
            CodeBlockTransformer(f, sys.stdout)()


if __name__ == '__main__':
    sys.exit(main())
