def calculate_pivot(high, low, close):

    pivot = (high + low + close) / 3

    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high

    r2 = pivot + (high - low)
    s2 = pivot - (high - low)

    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)

    return {
        "Pivot": round(pivot, 2),
        "R1": round(r1, 2),
        "R2": round(r2, 2),
        "R3": round(r3, 2),
        "S1": round(s1, 2),
        "S2": round(s2, 2),
        "S3": round(s3, 2)
    }


def calculate_cpr(high, low, close):

    pivot = (high + low + close) / 3
    bc = (high + low) / 2
    tc = (2 * pivot) - bc

    return {
        "TC": round(max(tc, bc), 2),
        "Pivot": round(pivot, 2),
        "BC": round(min(tc, bc), 2)
    }
