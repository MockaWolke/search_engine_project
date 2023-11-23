import os
from whoosh import index
from search_engine import INDEXES_DIR


def get_index_for_query(index_dir):
    index_dir = INDEXES_DIR / index_dir

    if not (os.path.isdir(index_dir) and os.listdir(index_dir)):
        raise ValueError(f"index_dir {index_dir} must exist and contain items.")

    # set index and writer
    return index.open_dir(index_dir)
