import timeit
import os
from helper_api.spellchecker import fix_spelling

queries = [
    "these are badly spelled",
    "wha am i doing here",
    "ome one what is ths",
    "blabla haha i sadsa",
    "this wont get netter",
    "what am ai doing",
    "also some loner qureies in here",
    "yes some much longe ones, blalbla!",
]


def loop_once():
    for q in queries:
        fix_spelling(q)


hundred_times = timeit.timeit(loop_once, number=100)

time_per_query = hundred_times / 100 / len(queries)

print(f"Took on average {time_per_query :.8f} seconds")
