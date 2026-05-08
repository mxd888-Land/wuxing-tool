def _reduce(n):
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def calculate_wuxing(year, month, day):
    y = f"{year:04d}"
    d = f"{day:02d}"
    m = f"{month:02d}"

    E = _reduce(int(d[0]) + int(d[1]))
    F = _reduce(int(m[0]) + int(m[1]))
    G = _reduce(int(y[0]) + int(y[1]))
    H = _reduce(int(y[2]) + int(y[3]))

    I = _reduce(E + F)
    J = _reduce(G + H)
    K = _reduce(I + J)

    elements = {
        1: '金', 6: '金',
        2: '水', 7: '水',
        3: '火', 8: '火',
        4: '木', 9: '木',
        5: '土',
    }
    return {'K': K, 'element': elements[K]}
