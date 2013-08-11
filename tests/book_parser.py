#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
from lxml import html


base_dir = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
with open(os.path.join(base_dir, 'book.html')) as f:
    raw_html = f.read()
parsed_html = html.fromstring(raw_html)


class CodeListing(object):
    COMMIT_REF_FINDER = r'^(.+) \((ch\d\dl\d\d\d\.?\d?)\)$'

    def __init__(self, filename, contents):
        self.is_server_listing = False
        if re.match(CodeListing.COMMIT_REF_FINDER, filename):
            self.filename = re.match(CodeListing.COMMIT_REF_FINDER, filename).group(1)
            self.commit_ref = re.match(CodeListing.COMMIT_REF_FINDER, filename).group(2)
        elif filename.startswith('server: '):
            self.filename = filename.replace('server: ', '')
            self.commit_ref = None
            self.is_server_listing = True
        else:
            self.filename = filename
            self.commit_ref = None
        self.contents = contents
        self.was_written = False
        self.skip = False

    @property
    def type(self):
        if any(l.count('@@') > 1 for l in self.contents.split('\n')):
            return 'diff'
        elif self.is_server_listing:
            return 'server code listing'
        elif self.commit_ref:
            return 'code listing with git ref'
        else:
            return 'code listing'

    def __repr__(self):
        return '<CodeListing %s: %s...>' % (self.filename, self.contents.split('\n')[0])



class Command(str):
    def __init__(self, a_string):
        self.was_run = False
        self.skip = False
        self.server_command = False
        str.__init__(a_string)

    @property
    def type(self):
        if self.server_command:
            return 'server command'
        for git_cmd in ('git diff', 'git status', 'git commit'):
            if git_cmd in self:
                return git_cmd
        if self.startswith('python') and 'test' in self:
            return 'test'
        if self == 'python3 manage.py syncdb':
            return 'interactive manage.py'
        if self == 'python3 manage.py collectstatic':
            return 'interactive manage.py'
        else:
            return 'other command'

    def __repr__(self):
        return '<Command %s>' % (str.__repr__(self),)




class Output(str):

    def __init__(self, a_string):
        self.was_checked = False
        self.skip = False
        str.__init__(a_string)

    @property
    def type(self):
        if u'├' in self:
            return 'tree'
        else:
            return 'output'



def parse_listing(listing):
    if  'sourcecode' in listing.get('class').split():
        filename = listing.cssselect('.title')[0].text_content().strip()
        contents = listing.cssselect('.content')[0].text_content().replace('\r\n', '\n').strip('\n')
        return [CodeListing(filename, contents)]

    else:
        commands = get_commands(listing)
        is_server_commands = False
        caption = listing.cssselect('div.title')
        if caption and caption[0].text_content().startswith('server command'):
            is_server_commands = True
            listing = listing.cssselect('div.content')[0]
        lines = listing.text_content().strip().replace('\r\n', '\n').split('\n')
        outputs = []
        output_after_command = ''
        for line in lines:
            line_start, hash, line_comments = line.partition(" #")
            commands_in_this_line = list(filter(line_start.strip().endswith, commands))
            if commands_in_this_line:
                if output_after_command:
                    outputs.append(Output(output_after_command.rstrip()))
                output_after_command = (hash + line_comments).strip()
                command = commands_in_this_line[0]
                if line_start.startswith('(virtualenv)'):
                    command = 'source ../virtualenv/bin/activate && ' + command
                command = Command(command)
                command.server_command = is_server_commands
                outputs.append(command)
            else:
                output_after_command += line + '\n'
        if output_after_command:
            outputs.append(Output(output_after_command.rstrip()))
        return outputs


def get_commands(node):
    commands = [
        el.text_content()
        for el in node.cssselect('pre code strong')
    ]
    if commands.count("git rm --cached superlists/"):
        ## hack -- listings with a star in are weird
        fix_pos = commands.index("git rm --cached superlists/")
        commands.remove("git rm --cached superlists/")
        commands.remove(".pyc")
        commands.insert(fix_pos, "git rm --cached superlists/*.pyc")

    return commands
