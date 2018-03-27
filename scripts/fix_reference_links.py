#!/usr/bin/env python
"""
Fix cross-reference links from before the conversion to Sphinx.

Usage:
    scripts/fix_reference_links.py <directory-name>

Scan a directory for .rst files and process them, finding and fixing links.
"""
# Plan:
#
# On scan():
# DONE: save (filename, pos, name, title) of every inline link
# DONE: save (filename, pos, name, title) of every Sphinx link reference
# DONE: save (filename, pos, name, title) of every explicit link target (label)
# DONE: save (filename, pos, name, title) of every section (implicit target)
#
# Report link refs without matching link target
# Report link targets with duplicate names (including implicit targets)
#
# On fix():
# For every referenced implicit target with unique generated name:
# Create an explicit target label for cross-document links
#
# For every link reference with a non-ambiguous target:
# Change the link from `title <#name>`__ format to :ref:`title <name>`
#
# Manually fix duplicate targets, then re-run this script till it runs clean.
from __future__ import print_function
from collections import defaultdict, namedtuple
import os
import re
import sys

import docopt


LinkInfo = namedtuple('LinkInfo', 'filename pos name title')


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

        # Possible section title marker
        r'^(?P<section_mark>(?P<markchar>[^A-Za-z0-9 \t])(?P=markchar){2,})$',
    ))

    def __init__(self):
        # map[name] = LinkInfo(filename, pos, name, title)
        self.link_map = defaultdict(list)
        self.ref_map = defaultdict(list)
        self.label_map = defaultdict(list)
        self.section_map = defaultdict(list)

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

    @classmethod
    def _find_section_title(cls, text, pos):
        """
        pos points to the start of what looks like a section marker.
        Scan backwards to see if the previous line looks like a section title.
        Return (title_pos, title) if found, else return (0, None).
        """
        # Looking for \n\n<text>\n
        # Or <start-of-doc><text>\n
        if pos < 2:
            # Not enough room for a title
            return 0, None
        # Section marker should be at start of line
        assert text[pos - 1] == '\n'
        i = text.rfind('\n\n', 0, pos - 1)
        if i < 0:
            i = 0
        else:
            i += 2
        title = text[i:pos - 1]
        if '\n' in title:
            # Title can only be one line
            return 0, None
        title = title.strip()
        if not title:
            return 0, None
        return i, title

    def scan(self, filename):
        """
        Process the reStructuredText in the file
        """
        with open(filename) as f:
            self._scan(filename, f)

    def _scan(self, filename, f):
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
                self.label_map[label].append(
                    LinkInfo(filename, pos, label, label))
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
                link_text = m.group('link_text')
                link_text = self.norm_link_text(link_text)
                link_info = LinkInfo(filename, pos, link_ref, link_text)
                self.link_map[link_ref].append(link_info)
                continue
            section_mark = self._group(m, 'section_mark')
            if section_mark:
                pos, section_title = self._find_section_title(text, pos)
                if not section_title or len(section_title) > len(section_mark):
                    continue
                name = self.norm_link_name(section_title)
                self.section_map[name].append(
                    LinkInfo(filename, pos, name, section_title))
                continue

    @classmethod
    def norm_link_text(cls, link_text):
        """
        Remove leading and trailing whitespace from link text
        Convert newlines to spaces
        """
        link_text = link_text.strip()
        link_text = re.sub(r'\r?\n', ' ', link_text)
        return link_text

    @classmethod
    def norm_link_name(cls, link_title):
        """
        Turn a link title into a link name:
        - strip leading and trailing whitespace
        - convert to lowercase
        - convert non-alphanumeric, non "-", characters to "-"
        - collapse repeated "-" characters
        - remove leading or trailing "-" characters
        """
        name = link_title.strip().lower()
        name = re.sub(r'[^a-z0-9-]', '-', name)
        name = re.sub(r'-+', '-', name)
        return name.strip('-')

    def report(self):

        def _count(map):
            count = 0
            for k, v in map.items():
                count += len(v)
            return count

        print("Number of inline links:", _count(self.link_map))
        print("Number of Sphinx references:", _count(self.ref_map))
        print("Number of link target labels:", _count(self.label_map))
        print("Number of section names (implicit targets):",
              _count(self.section_map))

        # Report known broken links
        # {filename: {name: [link_info, ...]}}
        implicit_targets = defaultdict(dict)
        for name, info_list in self.section_map.items():
            for link_info in info_list:
                implicit_targets[link_info.filename].setdefault(
                    name, []).append(link_info)
        broken_links = []
        ambiguous_links = []
        satisfied_links = []
        external_links = []
        for name, info_list in self.link_map.items():
            if name.startswith('#'):
                name = name[1:]
                for link_info in info_list:
                    filename = link_info.filename
                    if filename not in implicit_targets:
                        broken_links.append(link_info)
                        continue
                    if name not in implicit_targets[filename]:
                        broken_links.append(link_info)
                        continue
                    if len(implicit_targets[filename][name]) > 1:
                        ambiguous_links.append(link_info)
                        continue
                    satisfied_links.append((link_info,
                                            implicit_targets[filename][name]))
            else:
                external_links.extend(info_list)
        print(len(broken_links), "Broken links:")
        for link_info in broken_links:
            print(link_info)
        print(len(ambiguous_links), "Ambiguous links:")
        for link_info in ambiguous_links:
            print(link_info)
        print(len(satisfied_links), "Satisfied links:")
        for src, dst in satisfied_links:
            print(src, '->', dst)
        print(len(external_links), "External links:")
        for link_info in external_links:
            print(link_info)

        # Report on fixable links
        auto_fixable_links = []
        manual_fixable_links = []
        for link_info in broken_links:
            name = link_info.name.lstrip('#')
            targets = self.section_map.get(name, [])
            if not targets:
                continue
            if len(targets) == 1:
                auto_fixable_links.append((link_info, targets[0]))
            else:
                manual_fixable_links.append((link_info, targets))
        print(len(auto_fixable_links), "Automatically fixable links:")
        for src, dst in auto_fixable_links:
            print(src, '->', dst)
        print(len(manual_fixable_links), "Possible manually fixable links:")
        for src, dst in manual_fixable_links:
            print(src, '->', dst)


def process_dir(dirname):
    processor = LinkProcessor()
    for dirpath, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            if not filename.endswith('.rst'):
                continue
            filepath = os.path.join(dirpath, filename)
            print("Scanning", filepath)
            processor.scan(filepath)
    processor.report()


def main():
    args = docopt.docopt(__doc__)
    dirname = args['<directory-name>']
    process_dir(dirname)


if __name__ == '__main__':
    sys.exit(main())
