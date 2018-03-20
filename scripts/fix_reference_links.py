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
        r'^\.\. _(?P<label>[^:]+):$',
        r'``(?P<inline_code>.*?)``',
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

    def __call__(self, f):
        # Just read in the entire RST file
        text = f.read()
        line_num = 0  # XXX
        for m in re.finditer(self.PATTERN, text, re.MULTILINE):
            label = self._group(m, 'label')
            if label is not None:
                self.num_defs += 1
                print("Line:", line_num, "Label:", label)
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
                print("Line:", line_num, "Link:", refstr)
                continue

    @classmethod
    def standardize_link_text(cls, link_text):
        return XXX

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
