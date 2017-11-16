#!/usr/bin/env python
"""
Transform consecutive ".. code::" blocks into ".. language_specific::"
blocks in reStructuredText.
"""
from __future__ import print_function
import sys


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
        # Tabs counted as one indent character, oh well
        assert self.starting_indent is None
        self.starting_indent = len(line) - len(line.lstrip())
        assert not self.code_lines
        self.code_lines.append(line[self.starting_indent:])
        return self.state_scanning_code_block

    def state_scanning_code_block(self, line):
        indent = len(line) - len(line.lstrip())
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
        def _write(s, indent=0):
            self.out_fileobj.write(' ' * indent)
            self.out_fileobj.write(s)
        _write('.. language_specific::\n')
        for language, code_lines in code_blocks:
            _write('--{}\n'.format(language.capitalize()), indent=3)
            for code_line in code_lines:
                _write(code_line, indent=3)
        _write('\n')


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
    with open(sys.argv[1]) as f:
        CodeBlockTransformer(f, sys.stdout)()


if __name__ == '__main__':
    sys.exit(main())
