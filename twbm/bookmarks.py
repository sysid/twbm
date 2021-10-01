import logging
from typing import Sequence

from twbm.db.dal import Bookmark, DAL
from twbm.environment import config

_log = logging.getLogger(__name__)


class Bookmarks:
    bms: Sequence[Bookmark]

    def __init__(self, fts_query: str):
        self.fts_query = fts_query

        with DAL(env_config=config) as dal:
            self.bms = dal.get_bookmarks(fts_query=fts_query)

    @staticmethod
    def match_all(
        tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False
    ) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_all_tags(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_all_tags(tags, bm.split_tags)]
        return filtered

    @staticmethod
    def match_any(
        tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False
    ) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_any_tag(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_any_tag(tags, bm.split_tags)]
        return filtered

    @staticmethod
    def match_exact(
        tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False
    ) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_exact_tags(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_exact_tags(tags, bm.split_tags)]
        return filtered

    def filter(
        self,
        tags_all: str = None,
        tags_all_not: str = None,
        tags_any: str = None,
        tags_any_not: str = None,
        tags_exact: str = None,
    ):
        tags_all_ = normalize_tag_string(tags_all)
        tags_any_ = normalize_tag_string(tags_any)
        tags_all_not_ = normalize_tag_string(tags_all_not)
        tags_any_not_ = normalize_tag_string(tags_any_not)
        tags_exact_ = normalize_tag_string(tags_exact)

        # 0. over-rule
        if tags_exact is not None:
            self.bms = Bookmarks.match_exact(tags_exact_, self.bms)
        else:
            # 1. select viable
            if tags_all is not None:
                self.bms = Bookmarks.match_all(tags_all_, self.bms)

            if tags_any is not None:
                self.bms = Bookmarks.match_any(tags_any_, self.bms)

            # 2. narrow down
            if tags_any_not is not None:
                self.bms = Bookmarks.match_any(tags_any_not_, self.bms, not_=True)

            if tags_all_not is not None:
                self.bms = Bookmarks.match_all(tags_all_not_, self.bms, not_=True)
        return self.bms


def clean_tags(raw_tags: Sequence[str]) -> Sequence[str]:
    tags = set()
    tags_ = set(tag.strip().strip(",").lower() for tag in raw_tags)
    for tag in tags_:
        tags__ = set(t for t in tag.split(",") if t != ",")
        tags |= tags__
    tags = sorted(tags)
    _log.debug(f"cleaned tags: {tags}")
    return tags


def parse_tags(tags: Sequence[str]) -> str:
    tags = sorted(set((tag.lower().strip() for tag in tags)))
    return f",{','.join(tags)},"


def match_exact_tags(tags: Sequence, bm_tags: Sequence) -> bool:
    return set(bm_tags) == set(tags)


def match_all_tags(tags: Sequence, bm_tags: Sequence) -> bool:
    return (set(bm_tags) & set(tags)) == set(tags)


def match_any_tag(tags: Sequence, bm_tags: Sequence) -> bool:
    return len(set(bm_tags) & set(tags)) > 0


def check_tags(tags: Sequence[str]) -> Sequence[str]:
    with DAL(env_config=config) as dal:
        all_tags = set([r[0] for r in dal.get_all_tags()])
        return sorted((set(tags) - all_tags))


def normalize_tag_string(tag_string: str = None) -> Sequence[str]:
    if tag_string is None:
        tags_ = tuple()
    else:
        tags_ = tag_string.lower().replace(" ", "").split(",")
        tags_ = sorted(tag for tag in tags_ if tag != "")
    return tags_
