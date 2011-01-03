###############################################################################
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import sys

from nososql.lexer import Lexer
from nososql.parser import Parser


# program -> stat+
# stat -> table | insert | assign | query | print
#
# print -> 'print' expr ';'
# table -> 'create' 'table' ID '(' 'primary' 'key' ID (',' ID)+ ')' ';'
# insert -> 'insert' 'into' ID 'set' ID '=' expr ' (',' ID '=' expr)* ';'
# assign -> ID '=' expr ';'
# query -> 'select' ID (',' ID)* 'from' ID ('where' ID '=' expr)? ';'
# expr -> ID | STRING | INT | query


class Row(object):

    def __init__(self, columns):
        # columns: [(name, val), ...]
        self.columns = columns

    def _get_column_val(self, name):
        for col_name, col_val in self.columns:
            if col_name == name:
                return col_val

    def get_columns(self, column_names):
        result = []
        for name in column_names:
            val = self._get_column_val(name)
            result.append(val)

        return result

    def __iter__(self):
        return self.next()

    def next(self):
        for column in self.columns:
            yield column


class Table(object):

    def __init__(self, name, primary_key):
        self.name = name
        self.primary_key = primary_key
        self.columns = [primary_key]
        self.rows = {}

    def add_column(self, column):
        self.columns.append(column)

    def add(self, row):
        for col_name, col_val in row:
            # primary key value serves as a key in a dict
            if col_name == self.primary_key:
                self.rows[col_val] = row
                break

    def __str__(self):
        return 'Table = {name}, cols = {cols}, rows = {rows}'.format(
            name=self.name, cols=self.columns, rows=self.rows)


class Interpreter(object):

    def __init__(self):
        self.globals = {}
        self.tables = {}

    def create_table(self, name, primary_key, columns):
        table = Table(name, primary_key)
        for column in columns:
            table.add_column(column)
        self.tables[name] = table

    def insert_into(self, table_name, columns_meta):
        table = self.tables[table_name]
        row = Row(columns_meta)
        table.add(row)

    def select(self, table_name, columns, where_column=None, where_val=None):
        columns = [col.text for col in columns]
        table = self.tables[table_name]

        if table.primary_key == where_column:
            row = table.rows[where_val]
            result = row.get_columns(columns)
            return [result]

        # no primary key
        result = []
        for row in table.rows.values():
            result_row = row.get_columns(columns)
            result.append(result_row)

        return result

    def store(self, name, value):
        self.globals[name] = value

    def load(self, name):
        return self.globals[name]

    def print_(self, result):
        if isinstance(result, list):
            for row in result:
                for col in row:
                    print col,
                print
        else:
            print result


def main():
    if len(sys.argv) < 2:
        print 'usage: nososql [input file]'
        sys.exit()

    text = open(sys.argv[1]).read()

    lookahead_limit = 2
    interp = Interpreter()
    parser = Parser(Lexer(text), lookahead_limit, interp)
    parser.parse()



