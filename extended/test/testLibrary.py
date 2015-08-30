import sys
sys.path.append("..")

import stats.library as library

def testCalcHIndex():
    assert library.calcHIndex([]) == 0
    assert library.calcHIndex([0]) == 0
    assert library.calcHIndex([1]) == 1
    assert library.calcHIndex([1,2]) == 1
    assert library.calcHIndex([1,2,2]) == 2
    assert library.calcHIndex([2,3,1]) == 2
    assert library.calcHIndex([1,2,3,4,5]) == 3
    assert library.calcHIndex([23L,  0L,  0L,  2L,  20L,  1L,  13L, 1L,  3L,  3L,  4L,  1L,  9L,  2L,  8L,  7L,  0L,  24L,  4L, 2L, 5L, 1L, 4L, 0L, 3L, 0L, 1L, 0L, 1L, 4L, 1L, 0L, 0L, 1L, 1L, 1L, 1L, 1L, 13L, 0L, 0L, 1L, 1L, 0L, 1L, 1L, 9L, 7L, 2L, 0L, 0L, 0L, 1L, 0L, 1L, 1L, 2L, 0L, 0L, 0L, 0L, 0L, 0L, 2L, 11L, 0L, 0L, 6L, 1L, 0L, 10L, 1L, 1L, 0L, 0L, 1L, 9L, 42L, 1L, 1L, 1L, 0L, 1L, 1L, 1L, 0L, 1L, 1L, 0L, 1L, 0L, 2L, 2L, 1L, 0L, 1L, 0L, 9L, 11L, 1L, 0L, 1L, 1L, 2L, 2L, 1L, 1L, 0L]) == 9
    # assert library.calcHIndex(sa266) == 64

if __name__ == "__main__":
    testCalcHIndex()
