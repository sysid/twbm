import pytest

from twbm.twb import (
    _update_tags,
)


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
