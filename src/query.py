import os
from whoosh import index


def get_index_for_query(index_dir):
    if not (os.path.isdir(index_dir) and os.listdir(index_dir)):
        raise ValueError(f"index_dir {index_dir} must exist and contain items.")

    # set index and writer
    return index.open_dir(index_dir)
