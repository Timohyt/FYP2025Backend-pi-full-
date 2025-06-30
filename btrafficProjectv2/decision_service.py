def make_decision(lane: int, count: int) -> int:
    if count < 10:
        return 30
    elif 10 <= count <= 25:
        return 45
    else:
        return 60
