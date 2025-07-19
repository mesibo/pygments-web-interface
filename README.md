# Pygments Web Interface

Pygments is a powerful syntax highlighter written in Python that supports hundreds of languages and text formats. **Pygments Web Interface** provides a simple web-based frontend to [Pygments](https://pygments.org), allowing users to easily convert code snippets into beautifully formatted HTML which can be pasted in websites or documentation tools such as Google Docs or Slides without needing to write code or use command-line tools.

**Pygments Web Interface** is a fork of the original [hilite.me](http://hilite.me/) by [Mesibo](https://mesibo.com). The original code is very compact (two small Python files and one HTML template) but was unmaintained for 10+ years. We fixed it for internal use for [Mesibo real-time API](https://mesibo.com) and [PatANN Vector Database](https://patann.dev) documentation.

# Demo

[Demo](https://pygments-web-interface.onrender.com/)

## Changes in This Fork

- **Python 3 compatibility** - Updated from Python 2 to work with Python 3
- **Works with latest Pygments** - Compatible with current Pygments versions
- **Process id (pid) file** for proper cleanup
- **Bootstrap 5 based interface with AJAX** to update preview without page reload
- **Font detection** for preview
- **Local stoarge** for remembering last choices
- **Added font family and size adjustments**

## Security Considerations

⚠️ **Important**: This fork contains several security vulnerabilities from the original codebase that remain unfixed. These issues should be addressed if hosting this application publicly:

### Known Security Issues (Unfixed)

1. **Code Injection Risk**: The `get_lexer_by_name()` function accepts arbitrary user options that could potentially be exploited
2. **Regex Denial of Service (ReDoS)**: The line numbering regex `(<pre[^>]*>)(.*)(</pre>)` with `re.DOTALL` can cause catastrophic backtracking with malicious input
3. **CSS Injection/XSS**: User-controlled `divstyles` parameter is directly inserted into CSS without sanitization
4. **Resource Exhaustion**: No limits on input size or rate limiting to prevent abuse
5. **Information Disclosure**: Potential exposure of system information through error messages
6. **No Authentication in API**: The `/api` endpoint has no authentication or authorization controls

**Note**: Since this fork is intended for internal use only, these security issues were not prioritized for fixing. This code is provided AS-IS considering it will be useful to the development community for learning and internal projects.

## Development

To set up the development environment:

    % virtualenv env
    % source env/bin/activate
    % pip install -r requirements.txt
    % python main.py

The application will be available at `http://localhost:5000`.
