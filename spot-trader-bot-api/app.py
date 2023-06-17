import requests


def calculation(n):
    r = 0
    i = 1
    while i <= n:
        j = 1
        while j <= i:
            k = j
            while k <= i + j:
                l = 1
                while l <= i + j - k:
                    r = r + 1
                    l += 1
                k += 1
            j += 1
        i += 1
    return r


n = 5

for i in range(1, n + 1):
    print(f"n = {i} - r = {calculation(i)}")
