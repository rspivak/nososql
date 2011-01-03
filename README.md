NOSOSQL - Simple Syntax-Directed Interpreter for an SQL subset
==============================================================

Overview
--------

This is an example of a simple Syntax-Directed Interpreter
for a subset of SQL called NO-SO-SQL :)

For simplicity reasons database is created and manipulated in memory.

Installation
------------

Using `buildout`

    $ cd nososql
    $ python bootstrap.py
    $ bin/buildout

    Run the interpreter

    $ bin/nososql file_with_some_nososql


Technical details
-----------------

The interpreter is based on a Syntax-Directed Interpreter from
'Language Implementation Patterns' Ch.9

The main differences are:

1. Lexer is hand-crafted

2. LL(2) recursive-descent parser is hand-crafted

3. It's written in Python :)

4. The hash symbol can be used to comment out lines


High-level overview of the interpreter:

          +----------------+
          |                |
          |  Source code   |
          |                |
          +-------+--------+
                  |
                  |
                 \|/
          +----------------+
          |  Regexp-based  |
          |      Lexer     |
          |                |
          +-------+--------+
                  |
                  |
                 \|/
          +----------------+
          |LL(k) Recursive |
          | descent parser |
          | with embedded  |
          | actions        |
          +-------+--------+
                  |
                  |
                 \|/
               Output

SQL grammar:

    program -> stat+
    stat -> table | insert | assign | query | print

    print -> 'print' expr ';'
    table -> 'create' 'table' ID '(' 'primary' 'key' ID (',' ID)+ ')' ';'
    insert -> 'insert' 'into' ID 'set' ID '=' expr ' (',' ID '=' expr)* ';'
    assign -> ID '=' expr ';'
    query -> 'select' ID (',' ID)* 'from' ID ('where' ID '=' expr)? ';'
    expr -> ID | STRING | INT | query

    COMMENT -> #


Sample file test.nososql:

    create table test (primary key name, passwd, quota);
    insert into test set name='John', passwd='xxx', quota=100;
    insert into test set name='Jim', passwd='yyy', quota=200;
    insert into test set name='Test', passwd='test', quota=30;
    result = select passwd, quota from test where name='Jim';
    print result;

    $ bin/nososql test.nososql
    yyy 200


The goal of the project is self-education and to serve as a potential
example for people interested in crafting their own interpreter for
simple DSLs.


Development
-----------

Install 'enscript' utility (optional).
If you are on Ubuntu::

    $ sudo apt-get install enscript

Boostrap the buildout and run it:

    $ cd nososql
    $ python bootstrap.py
    $ bin/buildout

Run tests, test coverage and produce coverage reports::

    $ bin/test
    $ bin/coverage-test
    $ bin/coveragereport

    Check ./var/report/nososql.html out for coverage report.

Run pep8 and pylint to check code style and search for potential bugs:

    $ bin/pep8
    $ bin/pylint
