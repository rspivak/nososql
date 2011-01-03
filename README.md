NOSOSQL - Simple Syntax-Directed Interpreter for an SQL subset
==============================================================

Overview
--------

This is an example of a simple Syntax-Directed Interpreter
for a subset of SQL called NO-SO-SQL :)

For simplicity reasons database is created and manipulated in memory.

Sample file test.nososql:

    create table test (primary key name, age);
    insert into test set name='John', passwd='xxx', quota=100;
    insert into test set name='Jim', passwd='yyy', quota=200;
    insert into test set name='Test', passwd='test', quota=30;
    result = select passwd, quota from test where name='Jim';
    print result;


It's based on a Syntax-Directed Interpreter from
'Language Implementation Patterns' Ch.9

The main differences are:

1. Lexer is hand-crafted

2. Parser is hand-crafted

3. It's written in Python :)

4. The hash symbol can be used to comment out lines

The goal of the project is self-education and to serve as a potential
example for people interested in crafting their own interpreter for
simple DSLs.