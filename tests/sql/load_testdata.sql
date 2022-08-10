-- name: load_testdata!
insert into main.bookmarks (URL, metadata, tags, "desc", flags)
values ('http://xxxxx/yyyyy', 'TEST: entry for bookmark xxxx', ',ccc,xxx,yyy,', 'nice description b', 0),
       ('http://aaaaa/bbbbb', 'TEST: entry for bookmark bbbb', ',aaa,bbb,', 'nice description a', 0),
       ('http://asdf/asdf', 'bla blub', ',aaa,bbb,', 'nice description a2', 0),
       ('http://asdf2/asdf2', 'bla blub2', ',aaa,bbb,ccc,', 'nice description a3', 0),
       ('http://11111/11111', 'bla blub3', ',aaa,bbb,ccc,', 'nice description a4', 0),
       ('http://none/none', '', ',,', '', 0),
       ('/Users/Q187392', 'home', ',,', '', 0),
       ('$HOME/dev', 'dev', ',,', '', 0),
       ('$HOME/dev/py/twbm/tests/tests_data/tests.pptx', 'pptx', ',,', '', 0),
       ('shell::vim +/"## SqlAlchemy" $HOME/dev/py/twbm/tests/tests_data/sample_docu.md', 'shell open vim', ',,', '', 0)
       ;

