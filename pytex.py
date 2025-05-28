from __future__ import annotations
import os
from numbers import Number

PI = '\\pi'
LATEX = '\\LaTeX{}'


class _LaTeXDocument():
    """Class used to create a new LaTeX document"""

    def __init__(self, path, document_type, font_size, paper_type, title, author, thanks, date, make_title, opts):
        self.path = path
        self.document_type = document_type
        self.font_size = font_size
        self.paper_type = paper_type
        self.title = title
        self.author = author
        self.thanks = thanks
        self.date = date
        self.make_title = make_title
        self.opts = set([i.lower() for i in opts])

    def start_new_document(self):
        doc_class = f'\\documentclass[{self.font_size}pt, {self.paper_type}]{{%s}}\n\n' % self.document_type
        lines = [
            doc_class,
            '\\usepackage[utf8]{inputenc}\n'  # utf8 encoding
        ]

        if 'abnt' in self.opts:
            lines.append(
                '\\usepackage[alf, abnt-emphasize=bf, recuo=0cm, abnt-etal-cite=2, abnt-etal-list=0]{abntex2cite} % Citações padrão ABNT\n')
        if 'figures' in self.opts:
            lines.append('\\usepackage{graphicx}\n')
            if 'float' in self.opts:
                lines.append('\\usepackage{float}\n')
        if 'indentfirst' in self.opts:
            lines.append('\\usepackage{indentfirst}\n')

        lines.append('\n')

        if self.title:
            lines.append('\\title{%s}\n' % self.title)
        if self.author:
            if self.thanks:
                lines.append('\\author{%s\\thanks{%s}}\n' %
                             self.author % self.thanks)
            else:
                lines.append('\\author{%s}\n' % self.author)
        if self.date:
            lines.append('\\date{%s}\n' % self.date)

        lines.append('\\begin{document}\n')
        if self.make_title:
            lines.append('\\maketitle\n')
        lines.append('\\frenchspacing\n\n')

        return lines

    def write_document(self, lines: list[str]):
        if lines[-1] != '\\end{document}':
            lines.append('\\end{document}')
        with open(file=self.path, mode='w') as fp:
            fp.writelines(lines)


class PyTeX():
    """
    Class to convert python code to LaTeX formatting.

    `path`: path to latex document that will be written \\
    `document_type`: type of document (article, book, etc.) \\
    `font_size`: font size, default=12 \\
    `paper_type`: type of paper, default=a4paper (a4paper, letter, etc.) \\
    `title`: title of document, default=None
    `author`: author of document, default=None
    `thanks`: special thanks of document, default=None
    `date`: date of document, default=None
    `make_title`: whether or not to make title in document, default=False
    `opts`: miscellaneous options, default=[]

    `opts` are packages to be used, such as:
    * abnt: whether or not to include abntex2cite, writes according to ABNT (Associação Brasileira de Normas e Técnicas);
    * figures: whether or not to include graphicx for figures;
    * float: whether or not to include float for figures (must be used with figures);
    * indentfirst: whether or not to include indentfirst.
    """

    def __init__(self, path, document_type, font_size=12, paper_type='a4paper', title=None, author=None, thanks=None, date=None, make_title=False, opts=[]):
        self.document = _LaTeXDocument(path, document_type, font_size,
                                       paper_type, title, author, thanks, date, make_title, opts)
        self._content = self.document.start_new_document()

    def write_document(self):
        self.document.write_document(self._content)

    def _remove_end_content(self):
        if self._content[-1] == '\\end{document}':
            self._content.pop()

    def append_content(self, content: _LaTeXMath | str):
        """
        Function that appends `content` to the end document.
        """

        self._remove_end_content()

        inline: bool | None = None
        if isinstance(content, _LaTeXMath):
            inline = content.inline
            content = content.content

        if inline is not None:
            if inline:
                content = '\\begin{math}\n' + f'\t{content}\n' + '\\end{math}'
            else:
                content = '\\begin{equation}\n' + \
                    f'\t{content}\n' + '\\end{equation}'

        if not content.endswith('\n'):
            content += '\n'
        content += '\n'

        self._content.append(content)


class _LaTeXText():
    """Super class used for LaTeX text, not intended to be used alone."""
    
    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content
    
    def __repr__(self):
        return self.content
    
    def __add__(self, text: _LaTeXText | str):
        return _LaTeXText(self.content + str(text))
    
class Text(_LaTeXText):
    def __init__(self, content: str, emph: bool = False, bold: bool = False, underline: bool = False, italic: bool = False):
        if italic:
            content = '\\textit{%s}' % content
        if underline:
            content = '\\underline{%s}' % content
        if bold:
            content = '\\textbf{%s}' % content
        if emph:
            content = '\\emph{%s}' % content

        super().__init__(content)


class _LaTeXMath():
    """Super class used for LaTeX math, not intended to be used alone."""

    def __init__(self, content: str, inline: bool):
        self.content = content
        self.inline = inline

    def __str__(self):
        return self.content

    def __repr__(self):
        return self.content

    def __add__(self, math: _LaTeXMath | Number):
        return _LaTeXMath(self.content + str(math))

    def __neg__(self):
        return _LaTeXMath(f'-{self.content}', self.inline)


class Fraction(_LaTeXMath):
    def __init__(self, fraction: _LaTeXMath | str, inline: bool = False):
        """
        Class that allows the user to write a fraction in LaTeX.
        """
        
        n, d = str(fraction).split('/')

        content = '\\frac' + '{' + n.strip() + '}' + '{' + d.strip() + '}'

        super().__init__(content, inline)


class Sqrt(_LaTeXMath):
    def __init__(self, rooting: _LaTeXMath | str | Number, inline: bool = False):
        """
        Class that allows the user to write a square root in LaTeX.
        """

        content = '\\sqrt{' + str(rooting) + '}'

        super().__init__(content, inline)


class Integral(_LaTeXMath):
    def __init__(self, integrand: _LaTeXMath | Number | str, lower_limit: _LaTeXMath | Number | str | None = None, upper_limit: _LaTeXMath | Number | str | None = None, result: _LaTeXMath | Number | str | None = None, inline: bool = False):
        """
        Class that allows the user to write an integral in LaTeX, not including the dx*. \\
        You may include lower and upper limits and a result. \\
        The integral may be inline or not (default=not), auto-selected if the integral is an inner content. \\

        *You may also use other variables as well.
        """

        content = ''
        integrand = '{%s}' % str(integrand)

        if lower_limit is None and upper_limit is None:
            content += f'\\int {integrand}'
        elif lower_limit is not None and upper_limit is not None:
            lower_limit = '{%s}' % str(lower_limit)
            upper_limit = '{%s}' % str(upper_limit)
            content += f'\\int_{lower_limit}^{upper_limit} {integrand}'
        else:
            raise Exception(
                'Integral must have both lower limit and upper limit or neither.')

        if result:
            result = '{%s}' % str(result)
            content += f' = {result}'

        super().__init__(content, inline)
