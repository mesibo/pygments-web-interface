#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Pygments Web Interface
# 
# This is a fork of the original hilite.me by Mesibo (https://mesibo.com)
# GitHub Repository: https://github.com/mesibo/pygments-web-interface
#
# A simple web-based frontend to Pygments syntax highlighter, allowing users 
# to easily convert code snippets into beautifully formatted HTML which can 
# be pasted in websites or documentation tools such as Google Docs or Slides.
#
# Original Copyright © 2009-2011 Alexander Kojevnikov <alexander@kojevnikov.com>
# Fork maintained by Mesibo for internal use with Mesibo real-time API and 
# PatANN Vector Database documentation.
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import re

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def hilite_me(code, lexer, options, style, linenos, divstyles):
    lexer = lexer or 'python'
    style = style or 'colorful'
    defstyles = 'overflow:auto;width:auto;'

    formatter = HtmlFormatter(style=style,
                              linenos=False,
                              noclasses=True,
                              cssclass='',
                              cssstyles=defstyles + divstyles,
                              prestyles='margin: 0')
    html = highlight(code, get_lexer_by_name(lexer, **options), formatter)
    if linenos:
        html = insert_line_numbers(html)
    html = "<!-- HTML generated using hilite.me -->" + html
    return html

def get_default_style():
    return 'border:solid gray;border-width:.1em .1em .1em .8em;padding:.2em .6em;'

def insert_line_numbers(html):
    match = re.search('(<pre[^>]*>)(.*)(</pre>)', html, re.DOTALL)
    if not match: return html

    pre_open = match.group(1)
    pre = match.group(2)
    pre_close = match.group(3)

    html = html.replace(pre_close, '</pre></td></tr></table>')
    numbers = range(1, pre.count('\n') + 1)
    format = '%' + str(len(str(numbers[-1]))) + 'i'
    lines = '\n'.join(format % i for i in numbers)
    html = html.replace(pre_open, '<table><tr><td>' + pre_open + lines + '</pre></td><td>' + pre_open)
    return html
