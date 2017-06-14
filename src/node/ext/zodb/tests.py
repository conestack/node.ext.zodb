from interlude import interact
from pprint import pprint
import doctest
import unittest


optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE


TESTFILES = [
    '__init__.rst',
]


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            f,
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint},
        ) for f in TESTFILES
    ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')                 #pragma NO COVERAGE
