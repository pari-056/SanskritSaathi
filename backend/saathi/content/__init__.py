from . import level1, level2, level3, level4

LESSONS = level1.LESSONS + level2.LESSONS + level3.LESSONS + level4.LESSONS
BY_ID = {l.id: l for l in LESSONS}


def by_level(level: int):
    return [l for l in LESSONS if l.level == level]


def next_lesson_id(lesson_id: str):
    ids = [l.id for l in LESSONS]
    i = ids.index(lesson_id)
    return ids[i + 1] if i + 1 < len(ids) else None
