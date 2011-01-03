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

import unittest


class InterpreterTestCase(unittest.TestCase):

    def _parse(self, text, interpreter=None):
        from sonosql.interpreter import Interpreter
        from sonosql.lexer import Lexer
        from sonosql.parser import Parser

        lookahead_limit = 2

        interp = interpreter or Interpreter()
        parser = Parser(Lexer(text), lookahead_limit, interp)
        return parser.parse()

    def test_create_table(self):
        from sonosql.interpreter import Interpreter
        interp = Interpreter()
        self._parse('create table test (primary key name, age);', interp)

        self.assertTrue('test' in interp.tables, 'tables = %s' % interp.tables)

        self.assertEquals(interp.tables['test'].primary_key, 'name')

    def test_select_one_row(self):
        result = self._parse(
            """
            create table test (primary key name, age);
            insert into test set name='John', passwd='xxx', quota=100;
            select name, quota, passwd from test;
            """)

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0][0], 'John')
        self.assertEquals(result[0][1], 100)
        self.assertEquals(result[0][2], 'xxx')

    def test_select_multiple_rows(self):
        result = self._parse(
            """
            create table test (primary key name, age);
            insert into test set name='John', passwd='xxx', quota=100;
            insert into test set name='Jim', passwd='yyy', quota=200;
            select name, quota, passwd from test;
            """)

        self.assertEquals(len(result), 2)

    def test_select_where_clause(self):
        result = self._parse(
            """
            create table test (primary key name, age);
            insert into test set name='John', passwd='xxx', quota=100;
            insert into test set name='Jim', passwd='yyy', quota=200;
            insert into test set name='Test', passwd='test', quota=30;
            select passwd, quota from test where name='Jim';
            """)

        self.assertEquals(result[0][0], 'yyy')
        self.assertEquals(result[0][1], 200)

    def test_assign(self):
        from sonosql.interpreter import Interpreter
        interp = Interpreter()
        self._parse(
            """
            create table test (primary key name, age);
            insert into test set name='John', passwd='xxx', quota=100;
            result = select name from test;
            """, interp)

        self.assertEquals(interp.globals['result'], [['John']])

    def test_print(self):
        import sys
        import StringIO
        from contextlib import contextmanager

        @contextmanager
        def redirect_output():
            old = sys.stdout
            out = StringIO.StringIO()
            sys.stdout = out
            try:
                yield out
            finally:
                sys.stdout = old

        with redirect_output() as out:
            self._parse(
                """
                create table test (primary key name, age);
                insert into test set name='John', passwd='xxx', quota=100;
                result = select name from test;
                print result;
                """)

            self.assertEquals(out.getvalue().strip(), 'John')

    def test_comment(self):
        result = self._parse(
            """
            create table test (primary key name, age);
            insert into test set name='John', passwd='xxx', quota=100;
            #insert into test set name='Jim', passwd='yyy', quota=200;
            select name from test;
            """)

        self.assertEquals(len(result), 1)


