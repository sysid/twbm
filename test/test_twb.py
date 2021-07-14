import pytest

from twbm.twb import match_all_tags, match_any_tag, _update_tags, parse_tags, check_tags


@pytest.mark.parametrize(
    ("tags", "bm_tags", "result"),
    (
        (("a", "b"), ("a", "b", "c", "d"), True),
        (("a", "b"), ("b", "c", "d"), False),
        (("a", "b"), ("b", "a"), True),
        (("a", "b"), ("a",), False),
    ),
)
def test_match_all_tags(tags, bm_tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    assert match_all_tags(tags, bm_tags) is result


@pytest.mark.parametrize(
    ("tags", "bm_tags", "result"),
    (
        (("a", "b"), ("a", "b", "c", "d"), True),
        (("a", "b", "x"), ("a", "b", "c", "d"), True),
        (("a", "b", "x"), ("a",), True),
        (("a", "b"), ("x", "y"), False),
    ),
)
def test_match_any_tag(tags, bm_tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    assert match_any_tag(tags, bm_tags) is result


def test_match_all(dal):
    bms = dal.get_bookmarks(fts_query="")
    tags = ("aaa", "ccc")
    # filtered = [bm for bm in bms if 'web' in bm.tags.split(',')]
    filtered = [bm for bm in bms if match_all_tags(tags, bm.split_tags)]
    assert len(filtered) >= 1


def test_match_any(dal):
    bms = dal.get_bookmarks(fts_query="")
    tags = ("aaa", "xxx")
    # filtered = [bm for bm in bms if 'web' in bm.tags.split(',')]
    filtered = [bm for bm in bms if match_any_tag(tags, bm.split_tags)]
    assert len(filtered) >= 4


@pytest.mark.parametrize(
    ("ids", "tags", "tags_not", "force", "result"),
    (
        ((1,), ("x",), ("ccc",), False, ",x,xxx,yyy,"),
        ((1,), ("x",), None, True, ",x,"),
        ((1,), None, None, False, ",ccc,xxx,yyy,"),
        ((1,), None, ("ccc", "xxx", "yyy"), False, ",,"),
    ),
)
def test_update(dal, ids, tags, tags_not, result, force):
    # _update_tags((0,), ('x',), ('ob',))
    _update_tags(ids, tags, tags_not, force=force)
    assert dal.get_bookmarks(fts_query="xxxxx")[0].tags == result


@pytest.mark.parametrize(
    ("tags", "result"),
    (
        (("tag1", "tag2"), ",tag1,tag2,"),
        (("tag2", "tag1"), ",tag1,tag2,"),
        ((), ",,"),
    ),
)
def test_parse_tags(tags, result):
    assert parse_tags(tags) == result


@pytest.mark.parametrize(
    ("tags", "result"),
    (
        (("a", "b"), ["a", "b"]),
        (("xxx", "yyy"), []),
        (
            ("xxx", "yyy", "zzz"),
            [
                "zzz",
            ],
        ),
        ((), []),
    ),
)
def test_check_tags(dal, tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    unknown_tags = check_tags(tags)
    assert unknown_tags == result
    _ = None
