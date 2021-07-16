# -*- coding: utf-8 -*-
'''
Created on Sun May 2 16:23:26 2021

@author: Micah Jeroutek

==============================================================================
    Provides additional color options to be used in conjunction with the MCNP
    user defined language (UDL).
==============================================================================
'''
import sys
from Npp import (notepad, editor, editor1, editor2,
                 NOTIFICATION, SCINTILLANOTIFICATION,
                 INDICATORSTYLE, INDICFLAG, INDICVALUE)

if sys.version_info[0] == 2:
    from collections import OrderedDict as _dict
else:
    _dict = dict


class EnhanceLexer:

    def __init__(self):
        '''
            Initialize the class, should be called once only.
        '''

        current_version = notepad.getPluginVersion()
        if  current_version < '1.5.4.0':
            notepad.messageBox('It is needed to run PythonScript version 1.5.4.0 or higher',
                               'Unsupported PythonScript verion: {}'.format(current_version))
            return

        self.INDICATOR_ID = 0
        self.registered_lexers = _dict()

        self.document_is_of_interest = False
        self.regexes = None
        self.excluded_styles = None

        editor1.indicSetStyle(self.INDICATOR_ID, INDICATORSTYLE.TEXTFORE)
        editor1.indicSetFlags(self.INDICATOR_ID, INDICFLAG.VALUEFORE)
        editor2.indicSetStyle(self.INDICATOR_ID, INDICATORSTYLE.TEXTFORE)
        editor2.indicSetFlags(self.INDICATOR_ID, INDICFLAG.VALUEFORE)

        editor.callbackSync(self.on_updateui, [SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_marginclick, [SCINTILLANOTIFICATION.MARGINCLICK])
        notepad.callback(self.on_langchanged, [NOTIFICATION.LANGCHANGED])
        notepad.callback(self.on_bufferactivated, [NOTIFICATION.BUFFERACTIVATED])


    @staticmethod
    def rgb(r, g, b):
        '''
            Helper function
            Retrieves RGB color triple and converts it into its integer representation
            Args:
                r = integer, red color value in range of 0-255
                g = integer, green color value in range of 0-255
                b = integer, blue color value in range of 0-255
            Returns:
                RGB integer
        '''
        return (b << 16) + (g << 8) + r


    def register_lexer(self, lexer_name, _regexes, excluded_styles):
        '''
            reformat provided regexes and cache everything
            within registered_lexers dictionary.
            Args:
                lexer_name      = string, expected values as returned by notepad.getLanguageName
                                  without the "udf - " if it is an user defined language
                _regexes        = dict, in the form of
                                  _regexes[(int, (r, g, b))] = (r'', [int])
                excluded_styles = list of integers
            Returns:
                None
        '''
        regexes = _dict()
        for k, v in _regexes.items():
            regexes[(k[0], self.rgb(*k[1]) | INDICVALUE.BIT)] = v
        self.registered_lexers[lexer_name.lower()] = (regexes, excluded_styles)


    def paint_it(self, color, match_position, length, start_position, end_position):
        '''
            The text coloring function
            Args:
                color          = integer, expected in range of 0-16777215
                match_position = integer,  denotes the start position of a match
                length         = integer, denotes how many chars need to be colored.
                start_position = integer,  denotes the start position of the visual area
                end_position   = integer,  denotes the end position of the visual area
            Returns:
                None
        '''
        if (match_position + length < start_position or
            match_position > end_position or
            editor.getStyleAt(match_position) in self.excluded_styles):
            return

        editor.setIndicatorCurrent(0)
        editor.setIndicatorValue(color)
        editor.indicatorFillRange(match_position, length)


    def style(self):
        '''
            Calculates the text area to be searched for in the current document.
            Calls up the regexes to find the position and
            calculates the length of the text to be colored.
            Deletes the old indicators before setting new ones.
            Args:
                None
            Returns:
                None
        '''

        start_line = editor.docLineFromVisible(editor.getFirstVisibleLine())
        end_line = editor.docLineFromVisible(start_line + editor.linesOnScreen())
        if editor.getWrapMode():
            end_line = sum([editor.wrapCount(x) for x in range(end_line)])

        onscreen_start_position = editor.positionFromLine(start_line)
        onscreen_end_pos = editor.getLineEndPosition(end_line)

        editor.setIndicatorCurrent(0)
        editor.indicatorClearRange(0, editor.getTextLength())
        for color, regex in self.regexes.items():
            editor.research(regex[0],
                            lambda m: self.paint_it(color[1],
                                                    m.span(regex[1])[0],
                                                    m.span(regex[1])[1] - m.span(regex[1])[0],
                                                    onscreen_start_position,
                                                    onscreen_end_pos),
                                                    0,
                                                    onscreen_start_position,
                                                    onscreen_end_pos)

    def check_lexers(self):
        '''
            Checks if the current document of each view is of interest
            and sets the flag accordingly
            Args:
                None
            Returns:
                None
        '''

        current_language = notepad.getLanguageName(notepad.getLangType()).replace('udf - ','').lower()
        self.document_is_of_interest = current_language in self.registered_lexers
        if self.document_is_of_interest:
            self.regexes, self.excluded_styles = self.registered_lexers[current_language]


    def on_marginclick(self, args):
        '''
            Callback which gets called every time one clicks the symbol margin.
            Triggers the styling function if the document is of interest.
            Args:
                margin, only the symbol marign (=2) is of interest
            Returns:
                None
        '''
        if args['margin'] == 2 and self.document_is_of_interest :
            self.style()


    def on_bufferactivated(self, args):
        '''
            Callback which gets called every time one switches a document.
            Triggers the check if the document is of interest.
            Args:
                provided by notepad object but none are of interest
            Returns:
                None
        '''
        self.check_lexers()


    def on_updateui(self, args):
        '''
            Callback which gets called every time scintilla
            (aka the editor) changed something within the document.
            Triggers the styling function if the document is of interest.
            Args:
                provided by scintilla but none are of interest
            Returns:
                None
        '''
        if self.document_is_of_interest:
            self.style()


    def on_langchanged(self, args):
        '''
            Callback gets called every time one uses the Language menu to set a lexer
            Triggers the check if the document is of interest
            Args:
                provided by notepad object but none are of interest
            Returns:
                None
        '''
        self.check_lexers()


    def main(self):
        '''
            Main function entry point.
            Simulates two events to enforce detection of current document
            and potential styling.
            Args:
                None
            Returns:
                None
        '''
        self.on_bufferactivated(None)
        self.on_updateui(None)



# Usage:
#
#   Only the active document and for performance reasons, only the currently visible area
#   is scanned and colored.
#   This means, that a regular expression match is assumed to reflect only one line of code
#   and not to extend over multiple lines.
#   As an illustration, in python one can define, for example, a function like this
#
#       def my_function(param1, param2, param3, param4):
#           pass
#
#   but it is also valid to define it like this
#
#       def my_function(param1,
#                       param2,
#                       param3,
#                       param4):
#           pass
#
#   Now, if a regular expression like "(?:(?:def)\s\w+)\s*\((.+)\):" were used to color all parameters,
#   then this would only work as long as the line "def my_function(param1," is visible.
#
#   A possible approach to avoid this would be to define an offset range.
#
#   offset_start_line = start_line - offset
#   if offset_start_line < 0 then offset_start_line = 0
#
#   Not sure if this is the best approach - still investigating.
#
# Definition of colors and regular expressions
#   Note, the order in which a regular expressions will be processed is determined by its creation,
#   that is, the first definition is processed first, then the 2nd, and so on
#
#   The basic structure always looks like this
#
#       regexes[(a, b)] = (c, d)
#
#
#   regexes = an ordered dictionary which ensures that the regular expressions
#             are always processed in the same order.
#   a = an unique number - suggestion, start with 0 and always increase by one (per lexer)
#   b = color tuple in the form of (r,g,b). Example (255,0,0) for the color red.
#   c = raw byte string, describes the regular expression. Example r'\w+'
#   d = integer, denotes which match group should be considered


MCNP_regexes = _dict()

# Material cards - return match 0
MCNP_regexes[(1, (255, 0, 0))] = (r'm[0-9]+', 0)
MCNP_regexes[(2, (255, 0, 0))] = (r'M[0-9]+', 0)

MCNP_regexes[(3, (255, 0, 0))] = (r'mt[0-9]+', 0)
MCNP_regexes[(4, (255, 0, 0))] = (r'MT[0-9]+', 0)

MCNP_regexes[(5, (255, 0, 0))] = (r'mpn[0-9]+', 0)
MCNP_regexes[(6, (255, 0, 0))] = (r'MPN[0-9]+', 0)

MCNP_regexes[(7, (255, 0, 0))] = (r'mx[0-9]+', 0)
MCNP_regexes[(8, (255, 0, 0))] = (r'MX[0-9]+', 0)

# Changing "j" terms to green just like the rest of numbers - return match 0
MCNP_regexes[(12, (0, 0, 255))] = (r'j\h+', 0)
MCNP_regexes[(13, (0, 0, 255))] = (r'J\h+', 0)

# Changing "ilog" terms to green just like the rest of numbers - return match 0
MCNP_regexes[(52, (0, 0, 255))] = (r'[0-9]+ilog\h+', 0)
MCNP_regexes[(53, (0, 0, 255))] = (r'[0-9]+ILOG\h+', 0)

# Changing "T" terms to green just like the rest of numbers - return match 0
MCNP_regexes[(52, (0, 0, 255))] = (r'\h+t\h+', 0)
MCNP_regexes[(53, (0, 0, 255))] = (r'\h+T\h+', 0)

# Tallies, energy multipliers, time divisions, etc. - return match 0
MCNP_regexes[(34, (43, 151, 43))] = (r'fm[0-9]+', 0)
MCNP_regexes[(35, (43, 151, 43))] = (r'FM[0-9]+', 0)

MCNP_regexes[(36, (43, 151, 43))] = (r'fc.*', 0)
MCNP_regexes[(37, (43, 151, 43))] = (r'FC.*', 0)

MCNP_regexes[(38, (43, 151, 43))] = (r'f[0-9]+:', 0)
MCNP_regexes[(39, (43, 151, 43))] = (r'F[0-9]+:', 0)

MCNP_regexes[(40, (43, 151, 43))] = (r'^e[0-9]+', 0)
MCNP_regexes[(41, (43, 151, 43))] = (r'^E[0-9]+', 0)

MCNP_regexes[(8, (43, 151, 43))] = (r'em[0-9]+', 0)
MCNP_regexes[(9, (43, 151, 43))] = (r'EM[0-9]+', 0)

MCNP_regexes[(10, (43, 151, 43))] = (r't[0-9]+', 0)
MCNP_regexes[(11, (43, 151, 43))] = (r'T[0-9]+', 0)

MCNP_regexes[(14, (43, 151, 43))] = (r'fmesh[0-9]+', 0)
MCNP_regexes[(15, (43, 151, 43))] = (r'FMESH[0-9]+', 0)

MCNP_regexes[(16, (43, 151, 43))] = (r'tm[0-9]+', 0)
MCNP_regexes[(17, (43, 151, 43))] = (r'TM[0-9]+', 0)

MCNP_regexes[(18, (43, 151, 43))] = (r'cm[0-9]+', 0)
MCNP_regexes[(19, (43, 151, 43))] = (r'CM[0-9]+', 0)

MCNP_regexes[(20, (43, 151, 43))] = (r'cf[0-9]+', 0)
MCNP_regexes[(21, (43, 151, 43))] = (r'CF[0-9]+', 0)

MCNP_regexes[(22, (43, 151, 43))] = (r'sf[0-9]+', 0)
MCNP_regexes[(23, (43, 151, 43))] = (r'SF[0-9]+', 0)

MCNP_regexes[(24, (43, 151, 43))] = (r'fs[0-9]+', 0)
MCNP_regexes[(25, (43, 151, 43))] = (r'FS[0-9]+', 0)

MCNP_regexes[(26, (43, 151, 43))] = (r'sd[0-9]+', 0)
MCNP_regexes[(27, (43, 151, 43))] = (r'SD[0-9]+', 0)

MCNP_regexes[(28, (43, 151, 43))] = (r'fu[0-9]+', 0)
MCNP_regexes[(29, (43, 151, 43))] = (r'FU[0-9]+', 0)

MCNP_regexes[(30, (43, 151, 43))] = (r'ft[0-9]+', 0)
MCNP_regexes[(31, (43, 151, 43))] = (r'FT[0-9]+', 0)

MCNP_regexes[(32, (43, 151, 43))] = (r'cm[0-9]+', 0)
MCNP_regexes[(33, (43, 151, 43))] = (r'CM[0-9]+', 0)

# Fix for exponential terms (ex. 1.2e-3) - return match 0
MCNP_regexes[(42, (0, 0, 255))] = (r'[0-9]+e[0-9]+', 0)
MCNP_regexes[(43, (0, 0, 255))] = (r'[0-9]+E[0-9]+', 0)

MCNP_regexes[(44, (0, 0, 255))] = (r'[0-9]+e-[0-9]+', 0)
MCNP_regexes[(45, (0, 0, 255))] = (r'[0-9]+E-[0-9]+', 0)

MCNP_regexes[(46, (0, 0, 255))] = (r'[0-9]+e\+[0-9]+', 0)
MCNP_regexes[(47, (0, 0, 255))] = (r'[0-9]+E\+[0-9]+', 0)

# Colors in "xs", or cross section specifications - return match 0
MCNP_regexes[(50, (0, 109, 190))] = (r'xs[0-9]+', 0)
MCNP_regexes[(51, (0, 109, 190))] = (r'XS[0-9]+', 0)

# Grays out lines that start with c is followed by whitespace - return match 0
MCNP_regexes[(48, (153, 153, 153))] = (r'\nc\h+.*', 0)
MCNP_regexes[(49, (153, 153, 153))] = (r'\nC\h+.*', 0)


# There is no standardization in defining the style IDs of lexers attributes,
# hence one has to check the stylers.xml (or THEMENAME.xml) to see which
# IDs are defined by the respective lexer and what its purposes are to
# create an list of style ids which shouldn't be altered.
MCNP_excluded_styles = [1, 4, 6, 7, 12, 13, 14, 15, 16, 23]

# user defined lexers
# Definition of which area should not be styled
# 0 = default style
# 1 = comment style
# 2 = comment line style
# 3 = numbers style
# 4 = keyword1 style
# ...
# 11 = keyword8 style
# 12 = operator style
# 13 = fold in code 1 style
# 14 = fold in code 2 style
# 15 = fold in comment style
# 16 = delimiter1 style
# ...
# 23 = delimiter8 style
# excluded_styles = [1, 2, 16, 17, 18, 19, 20, 21, 22, 23]

_enhance_lexer = EnhanceLexer()

_enhance_lexer.register_lexer('MCNP', MCNP_regexes, MCNP_excluded_styles)

# start
_enhance_lexer.main()
