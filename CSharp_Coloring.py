
import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

# Coloring, formating function
def format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
       'keyword': format('blue'),
       'operator': format('green'),
       'brace': format('green'),
       'class': format('blue', 'bold'),
       'string': format('red'),
       'string2': format('darkMagenta'),
       'comment': format('darkGreen', 'italic'),
       'classID': format('black', 'italic'),
       'numbers': format('red'),
       'builtInFunctions': format('green'),
       'dataTypes': format('magenta'),
       'logicalOperators': format('green')
   }

class CSharpHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the C# language.
    """
    # C# keywords
    keywords = [
       "public","private","protected","internal","protected","internal","using",
       "abstract","async","const","event","extern","new","override","partial",
       "readonly","sealed","static","unsafe","virtual","volatile","if","else","true",
       "class","false","switch","case","default","break","continue",
       "for","foreach","while","do","try","catch","finally","in","void","delegate","Console"
    ]
    
    #built in functions
    builtInFunctions = [
        "ToBoolean","ToByte","ToChar","ToDateTime","ToDecimal","ToDouble","ToInt32","ToInt64",
        "ToSbyte","ToSingle","ToString","ToType","ToUInt32","ToUInt64",
         "sizeof","typeof","is","as","AsInt","IsInt","AsFloat",
         "IsFloat","AsDecimal","IsDecimal","AsDateTime","IsDateTime","AsBool","IsBool","Clone","CompareTo",
         "Contains","EndsWith","Equals","GetHashCode","GetType","IndexOf","ToLower","ToUpper",
         "Insert","IsNormalized","LastIndexOf","Length","Remove","Split","Replace","StartsWith","ToCharArray","Trim",
         "IsFixedSize","LongLength","TrueForAll"
         "BinarySearch","Clear","Clone","Copy","CopyTo","Empty","CreateInstance","Exists","find","FindIndex",
         "FindAll","GetEnumerator","GetType","Initialize","Resize","Reverse","Sort","ToString"
    ]
    
    #data types
    dataTypes = [
        "int","double","float","String","char","byte","long","decimal","bool","enums","struct"
    ]

    # C# operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '\%',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=','&=',
        # Bitwise
        '\^', '\|', '\&', '\~',
        #shift
        '<<=','<<='
             
    ]
    
    # Logical and Bitwise Operators
    logicalOperators = [
        # logicalOperators
        '&&','\|\|', '!','<<','>>'
    ]

    # braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)
        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in CSharpHighlighter.keywords]
        
        rules += [(r'\b%s\b' % w, 0, STYLES['dataTypes'])
                  for w in CSharpHighlighter.dataTypes]
        
        rules += [(r'\b%s\b' % w, 0, STYLES['builtInFunctions'])
                  for w in CSharpHighlighter.builtInFunctions]
        
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in CSharpHighlighter.operators]

        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in CSharpHighlighter.braces]
        
        rules += [(r'%s' % b, 0, STYLES['logicalOperators'])
                  for b in CSharpHighlighter.logicalOperators]


        # All other rules
        rules += [
            # 'class'
            (r'\bclass\b', 0, STYLES['class']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['classID']),

            # From '//' until a newline
            (r'//[^\n]*', 0, STYLES['comment']),
            
            # From '//' until a newline
            #(r'/*[^\n]*/*', 0, STYLES['comment']),


            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.matchMultiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.matchMultiline(text, *self.tri_double)

    def matchMultiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False