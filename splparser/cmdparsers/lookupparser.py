#!/usr/bin/env python

import imp
import logging
import os
import ply.yacc

from splparser.parsetree import *
from splparser.exceptions import SPLSyntaxError

from splparser.cmdparsers.common.fieldrules import *
from splparser.cmdparsers.common.fieldlistrules import *
from splparser.cmdparsers.common.valuerules import *

from splparser.cmdparsers.lookuplexer import lexer, tokens

PARSETAB_DIR = 'parsetabs'
PARSETAB = 'lookup_parsetab'

start = 'cmdexpr'

def p_cmdexpr_lookup(p):
    """cmdexpr : lookupcmd"""
    p[0] = p[1]

def p_lookup_tablename(p):
    """lookupcmd : LOOKUP table"""
    p[0] = ParseTreeNode('LOOKUP')
    p[0].add_children(p[2])

def p_lookup_options_tablename(p):
    """lookupcmd :  LOOKUP field EQ value table"""
    p[0] = ParseTreeNode('LOOKUP')
    option = ParseTreeNode(p[2].raw.upper())
    boolean = p[4]
    option.add_child(boolean)
    p[0].add_children([option] + p[5])

def p_table_tablename(p):
    """table : fieldlist"""
    p[0] = p[1].children

def p_table_tablename_field_output(p):
    """table : fieldlist out"""
    table = p[1].children
    table.append(p[2])
    p[0] = table

def p_field_as(p):
    """field : field ASLC fieldlist
             | field ASUC fieldlist"""
    _as = ParseTreeNode('AS')
    _as.add_children(p[3].children)
    p[1].add_child(_as)
    p[0] = p[1]

def p_out(p):
    """out : OUTPUT fieldlist
           | OUTPUTNEW fieldlist"""
    p[0] = ParseTreeNode(p[1])
    p[0].add_children(p[2].children)

def p_error(p):
    raise SPLSyntaxError("Syntax error in lookup parser input!")

logging.basicConfig(
    level = logging.DEBUG,
    filename = "lookupparser.log",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)

log = logging.getLogger()

def parse(data, ldebug=False, ldebuglog=log, pdebug=False, pdebuglog=log):
    here = os.path.dirname(__file__)
    path_to_parsetab = os.path.join(here, PARSETAB_DIR, PARSETAB + '.py')
    
    try:
        parsetab = imp.load_source(PARSETAB, path_to_parsetab)
    except IOError: # parsetab files don't exist in our installation
        parsetab = PARSETAB

    try:
        os.stat(PARSETAB_DIR)
    except:
        try:
            os.makedirs(PARSETAB_DIR)
        except OSError:
            sys.stderr.write("ERROR: Need permission to write to ./" + PARSETAB_DIR + "\n")
            raise

    parser= ply.yacc.yacc(debug=pdebug, debuglog=pdebuglog, tabmodule=parsetab, outputdir=PARSETAB_DIR)
    return parser.parse(data, debug=pdebuglog, lexer=lexer)

if __name__ == "__main__":
    import sys
    lexer = ply.lex.lex()
    parser = ply.yacc.yacc()
    print parser.parse(sys.argv[1:], debug=log, lexer=lexer)