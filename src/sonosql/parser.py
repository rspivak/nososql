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

from sonosql import tokens


class ParserException(Exception):
    pass


class Parser(object):
    """SO NO SQL Parser class.

    Parser calls into interpreter to do the 'real' work.
    """

    def __init__(self, lexer, lookahead_limit, interpreter):
        self.lexer = lexer
        self.lookahead = [None] * lookahead_limit
        self.lookahead_limit = lookahead_limit
        self.pos = 0
        self._init_lookahead()
        self.interpreter = interpreter

    def parse(self):
        result = None

        while self._lookahead_type(0) != tokens.EOF:

            token_type = self._lookahead_type(0)

            if (token_type == tokens.ID and
                self._lookahead_type(1) == tokens.EQUALS
                ):
                self._assign()
            elif token_type == tokens.PRINT_KW:
                self._print()
            elif token_type == tokens.CREATE_KW:
                self._table()
            elif token_type == tokens.INSERT_KW:
                self._insert()
            elif token_type == tokens.SELECT_KW:
                result = self._query()

        return result

    def _print(self):
        """Print rule

        print -> 'print' expr ';'
        """
        self._match(tokens.PRINT_KW)
        self.interpreter.print_(self._expr())
        self._match(tokens.SEMICOLON)

    def _assign(self):
        """Assign rule.

        assign -> ID '=' expr ';'
        """
        name = self._lookahead_token(0).text
        self._match(tokens.ID)
        self._match(tokens.EQUALS)
        value = self._expr()

        self.interpreter.store(name, value)

    def _table(self):
        """Table rule.

        table -> 'create' 'table' ID '(' 'primary' 'key' ID (',' ID)+ ')' ';'
        """
        columns = []

        self._match(tokens.CREATE_KW)
        self._match(tokens.TABLE_KW)

        table_name = self._lookahead_token(0).text

        self._match(tokens.ID)
        self._match(tokens.LPAREN)
        self._match(tokens.PRIMARY_KW)
        self._match(tokens.KEY_KW)
        primary_key = self._lookahead_token(0).text

        self._match(tokens.ID)

        while self._lookahead_type(0) == tokens.COMMA:
            self._match(tokens.COMMA)
            column = self._lookahead_token(0).text
            columns.append(column)
            self._match(tokens.ID)

        self._match(tokens.RPAREN)
        self._match(tokens.SEMICOLON)

        # invoke action
        self.interpreter.create_table(table_name, primary_key, columns)

    def _insert(self):
        """Insert rule.

        insert -> 'insert' 'into' ID 'set' ID '=' expr ' (',' ID '=' expr)* ';'
        """
        columns = []

        self._match(tokens.INSERT_KW)
        self._match(tokens.INTO_KW)

        table_name = self._lookahead_token(0).text
        self._match(tokens.ID)

        self._match(tokens.SET_KW)
        column_name = self._lookahead_token(0).text
        self._match(tokens.ID)
        self._match(tokens.EQUALS)

        column_val = self._expr()
        columns.append((column_name, column_val))

        while self._lookahead_type(0) == tokens.COMMA:
            self._match(tokens.COMMA)
            column_name = self._lookahead_token(0).text
            self._match(tokens.ID)
            self._match(tokens.EQUALS)
            column_val = self._expr()
            columns.append((column_name, column_val))

        self._match(tokens.SEMICOLON)

        # invoke action
        self.interpreter.insert_into(table_name, columns)

    def _query(self):
        """Query rule.

        query -> 'select' ID (',' ID)* 'from' ID ('where' ID '=' expr)? ';'
        """
        columns = []

        self._match(tokens.SELECT_KW)
        columns.append(self._lookahead_token(0))
        self._match(tokens.ID)

        while self._lookahead_type(0) == tokens.COMMA:
            self._match(tokens.COMMA)
            column = self._lookahead_token(0)
            self._match(tokens.ID)
            columns.append(column)

        self._match(tokens.FROM_KW)
        table_name = self._lookahead_token(0).text
        self._match(tokens.ID)

        if self._lookahead_type(0) != tokens.WHERE_KW:
            self._match(tokens.SEMICOLON)
            return self.interpreter.select(table_name, columns)

        # Handle WHERE clause
        self._match(tokens.WHERE_KW)

        where_column = self._lookahead_token(0).text
        self._match(tokens.ID)

        self._match(tokens.EQUALS)

        expr_result = self._expr()
        self._match(tokens.SEMICOLON)

        result = self.interpreter.select(
            table_name, columns,
            where_column=where_column, where_val=expr_result)

        return result

    def _expr(self):
        """Expression rule.

        expr -> ID | STRING | INT | query
        """
        token = self._lookahead_token(0)
        token_type = token.type
        if token_type == tokens.ID:
            self._match(tokens.ID)
            return self.interpreter.load(token.text)

        if token_type == tokens.STRING:
            self._match(tokens.STRING)
            return token.text.strip("'")

        if token_type == tokens.INT:
            self._match(tokens.INT)
            return int(token.text)

        return self._query()

    def _init_lookahead(self):
        for _ in range(self.lookahead_limit):
            self._consume()

    def _match(self, token_type):
        if self._lookahead_type(0) == token_type:
            self._consume()
        else:
            raise ParserException(
                'Expecting %s; found %s' % (
                    token_type, self._lookahead_token(0))
                )

    def _consume(self):
        self.lookahead[self.pos] = self.lexer.token()
        self.pos = (self.pos + 1) % self.lookahead_limit

    def _lookahead_type(self, number):
        return self._lookahead_token(number).type

    def _lookahead_token(self, number):
        return self.lookahead[(self.pos + number) % self.lookahead_limit]
