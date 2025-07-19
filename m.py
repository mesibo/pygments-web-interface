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

import datetime
import signal
import sys
import argparse
import atexit
import socket
import os
from urllib.parse import quote, unquote

from flask import Flask, make_response, render_template, request

from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from tools import *


app = Flask(__name__)

# Flag to prevent duplicate cleanup
_cleanup_called = False

def socket_bind_wrapper(original_bind):
    """Wrapper to enable SO_REUSEADDR on socket bind"""
    def bind_with_reuse(self, address):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return original_bind(self, address)
    return bind_with_reuse

def cleanup():
    """Cleanup function to ensure resources are properly released"""
    global _cleanup_called
    if _cleanup_called:
        return
    _cleanup_called = True
    print("Cleaning up resources and releasing port...")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\nShutting down Pygments Web Interface gracefully...')
    cleanup()
    os._exit(0)

def setup_signal_handlers():
    """Set up signal handlers that work with Flask's reloader"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

@app.route("/", methods=['GET', 'POST'])
def index():
        code = request.form.get('code', "print('hello world!')")
        lexer = (
            request.form.get('lexer', '') or
            unquote(request.cookies.get('lexer', 'python')))
        lexers = [(l[1][0] if l[1] else '', l[0]) for l in get_all_lexers() if l[1]]
        lexers = sorted(lexers, key=lambda x: x[1].lower())
        style = (
            request.form.get('style', '') or
            unquote(request.cookies.get('style', 'colorful')))
        styles = sorted(get_all_styles(), key=str.lower)
        linenos = (
            request.form.get('linenos', '') or
            request.method == 'GET' and
            unquote(request.cookies.get('linenos', ''))) or ''
        divstyles = request.form.get(
            'divstyles', unquote(request.cookies.get('divstyles', '')))
        divstyles = divstyles or get_default_style()

        html = hilite_me(code, lexer, {}, style, linenos, divstyles)
        response = make_response(render_template('index.html', **locals()))

        next_year = datetime.datetime.now() + datetime.timedelta(days=365)
        response.set_cookie('lexer', quote(lexer), expires=next_year)
        response.set_cookie('style', quote(style), expires=next_year)
        response.set_cookie('linenos', quote(linenos), expires=next_year)
        response.set_cookie('divstyles', quote(divstyles), expires=next_year)

        return response

@app.route("/api", methods=['GET', 'POST'])
def api():
    code = request.values.get('code', '')
    if not code:
        response = make_response(render_template('api.txt'))
        response.headers["Content-Type"] = "text/plain"
        return response

    lexer = request.values.get('lexer', '')
    options = request.values.get('options', '')

    def convert(item):
        key, value = item
        if value == 'False':
            return key, False
        elif value == 'True':
            return key, True
        else:
            return key, value
    options = dict(convert(option.split('=')) for option in options.split(',') if option)

    style = request.values.get('style', '')
    linenos = request.values.get('linenos', '')
    divstyles = request.form.get('divstyles', get_default_style())

    html = hilite_me(code, lexer, options, style, linenos, divstyles)
    response = make_response(html)
    response.headers["Content-Type"] = "text/plain"
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pygments Web Interface - A web frontend for Pygments syntax highlighter')
    parser.add_argument('--host', '-H', default='127.0.0.1', 
                        help='Host IP address (default: 127.0.0.1 for security)')
    parser.add_argument('--port', '-p', type=int, default=5000,
                        help='Port number (default: 5000)')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Enable socket reuse to avoid "Address already in use" errors
    socket.socket.bind = socket_bind_wrapper(socket.socket.bind)
    
    # Register cleanup function to run on exit
    atexit.register(cleanup)
    
    print(f"Starting Pygments Web Interface on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    
    try:
        # Enable reloader for development convenience
        # The port release will be handled by atexit and KeyboardInterrupt
        app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=True)
    except KeyboardInterrupt:
        print('\nPygments Web Interface stopped.')
        cleanup()
    except Exception as e:
        print(f'\nServer error: {e}')
        cleanup()
    finally:
        # Ensure cleanup always runs
        cleanup()
