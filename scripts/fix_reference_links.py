#!/usr/bin/env python
"""
Fix cross-reference links from before the conversion to Sphinx.

Usage:
    scripts/fix_reference_links.py <directory-name>

Scan a directory for .rst files and process them, finding and fixing links.
"""
from __future__ import print_function
import os
import re
import sys

import docopt


class LinkProcessor(object):

    PATTERN = '|'.join((
        # Sphinx link targets: .. _<label>:
        r'^\.\. _(?P<label>[^:]+):$',

        # reStructuredText directives:
        # .. directive_name:: (followed by indented lines)
        r'^\.\. (?P<directive>[^:]+)::$',

        # Inline code snippets: ``print(a + 2)``
        r'``(?P<inline_code>.*?)``',

        # Link references: `Link text <#target>`__
        r'`(?P<link_text>[^<]*?)\s*?<(?P<link_ref>[^>]+?)>`_{1,2}',
    ))

    def __init__(self):
        self.num_defs = 0
        self.num_refs = 0

    @classmethod
    def _group(cls, m, group_id):
        try:
            return m.group(group_id)
        except IndexError:
            return None

    @classmethod
    def _skip_indented_lines(cls, text, pos):
        """
        Scan text starting at the first line after position pos.
        Search for the first non-indented, non-blank line. Return the position
        of the start of that line.  Return len(text) if no such line is found.
        """
        # Scan to end of current line or end of string, whichever is first.
        m = re.search('$', text[pos:], flags=re.MULTILINE)
        pos += m.end()
        m = re.search(r'^\S', text[pos:], flags=re.MULTILINE)
        if not m:
            # Non-blank, non-indented line not found
            return len(text)
        pos += m.start()
        return pos

    def __call__(self, f):
        """
        Process the reStructuredText in file object f
        """
        # Just read in the entire RST file
        text = f.read()
        skip_to_pos = None
        for m in re.finditer(self.PATTERN, text, re.MULTILINE):
            pos = m.start()
            if skip_to_pos is not None:
                if pos < skip_to_pos:
                    continue
                skip_to_pos = None
            label = self._group(m, 'label')
            if label is not None:
                self.num_defs += 1
                print("Position:", pos, "Label:", label)
                continue
            directive = self._group(m, 'directive')
            if directive is not None:
                skip_to_pos = self._skip_indented_lines(text, pos)
                continue
            inline_code = self._group(m, 'inline_code')
            if inline_code is not None:
                continue
            link_ref = self._group(m, 'link_ref')
            if link_ref is not None:
                self.num_refs += 1
                link_text = m.group('link_text')
                link_text = self.standardize_link_text(link_text)
                refstr = '"{}" {}'.format(link_text, link_ref)
                print("Position:", pos, "Link:", refstr)
                continue

    @classmethod
    def standardize_link_text(cls, link_text):
        """
        Remove leading and trailing whitespace from link text
        Convert newlines to spaces
        """
        link_text = link_text.strip()
        link_text = re.sub(r'\r?\n', ' ', link_text)
        return link_text

    def close(self):
        print("Number of link target labels:", self.num_defs)
        print("Number of link references:", self.num_refs)


def process_dir(dirname):
    processor = LinkProcessor()
    for dirpath, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            if not filename.endswith('.rst'):
                continue
            filepath = os.path.join(dirpath, filename)
            print("Processing", filepath)
            with open(filepath) as f:
                processor(f)
    processor.close()


def main():
    args = docopt.docopt(__doc__)
    dirname = args['<directory-name>']
    process_dir(dirname)


if __name__ == '__main__':
    sys.exit(main())
