from __future__ import absolute_import

import sys
import os
import subprocess

import pytest

import opm.io

from subscript.eclcompress import eclcompress as eclc


FILELINES = [
    "GRIDUNIT",
    "'METRES ' '    ' /",
    "",
    " SATNUM  ",
    "0 0   0 1 1 1 3 1 4 3 2",
    "0 0 1 1 1 1 1 1 1 1 1 1 2" " 0 4 1 /",
    "IMBNUM",
    "0 0 3 3 2 2 2 2",
    "/ --something at the end we want to preserve",
    "SWOF",
    "-- A comment we dont want to mess up",
    "-- here is some data that is commented out",
    "0 0 1 0",
    "0.5 0.5 0.5 0",
    "1   1  0 0",
    "/",
    "-- A comment with slashes /which/must/be/preserved as comment",  # noqa
    "PORO  0 0 0 / ",
    "PERMY",
    "0 0 0 / -- more comments after ending slash, destroys compression",  # noqa
    "",
    "EQUALS",
    "MULTZ 0.017101  1 40  1 64  5  5 / nasty comment without comment characters"  # noqa
    "/",
]


def test_cleanlines():
    assert eclc.cleanlines([" PORO"]) == ["PORO"]
    assert eclc.cleanlines(["PORO 3"]) == ["PORO", "3"]
    assert eclc.cleanlines(["PORO 1 2 3 /"]) == ["PORO", "1 2 3 ", "/"]
    assert eclc.cleanlines([" PORO/"]) == ["PORO", "/"]
    assert eclc.cleanlines([" PORO/  foo"]) == ["PORO", "/", "  -- foo"]
    assert eclc.cleanlines(["-- PORO 4"]) == ["-- PORO 4"]
    assert eclc.cleanlines(["POROFOOBARCOM  4"]) == ["POROFOOBARCOM  4"]


def test_find_keyword_sets():
    assert eclc.find_keyword_sets(["PORO", "0 1 2 3", "4 5 6", "/"]) == [(0, 3)]


def test_compress_multiple_keywordsets():
    filelines = ["PORO", "0 0 0 3", "4 5 6", "/"]
    kwsets = eclc.find_keyword_sets(filelines)
    assert eclc.compress_multiple_keywordsets(kwsets, filelines) == [
        "PORO",
        "3*0 3 4 5 6",
        "/",
    ]


def test_eclcompress():
    cleaned = eclc.cleanlines(FILELINES)
    kwsets = eclc.find_keyword_sets(cleaned)
    compressed = eclc.compress_multiple_keywordsets(kwsets, cleaned)
    compressedstr = "\n".join(compressed)

    # Feed the compressed string into opm.io. OPM hopefully chokes on whatever
    # Eclipse would choke on (and hopefully not on more..)
    parsecontext = opm.io.ParseContext(
        [("PARSE_MISSING_DIMS_KEYWORD", opm.io.action.ignore)]
    )
    assert opm.io.Parser().parse_string(compressedstr, parsecontext)


@pytest.mark.integration
def test_integration():
    """Test endpoint is installed"""
    assert subprocess.check_output(["eclcompress", "-h"])


def test_vfpprod(tmpdir):
    """VFPPROD contains multiple record data, for which E100
    fails if the record-ending slash is not on the same line as the data
    """
    tmpdir.chdir()
    vfpstr = """
VFPPROD
  10 2021.3 LIQ WCT GOR THP GRAT METRIC BHP /
  50 150 300 500 1000 1500 2000 3000 4000 5000 6500 8000 10000 /
  50 100 150 200 250 300 400 500 /
  0 0.1 0.2 0.3 0.4 0.5 0.65 0.8 0.95 /
  300 332 350 400 500 1000 2000 5000 10000 30000 /
  0 /
  1 1 1 1
  50.35 50.32 50.34 50.36 50.8 52.03 53.91 58.73 64.01 69.69 78.1 86.34 97.46 /
  1 1 2 1
  50.34 50.31 50.34 50.36 50.85 52.38 54.45 59.58 65.46 71.53 80.43 89.28 101.43 /
  1 1 3 1
"""
    parsecontext = opm.io.ParseContext(
        [("PARSE_MISSING_DIMS_KEYWORD", opm.io.action.ignore)]
    )
    # Confirm that OPM can parse the startiing point:
    assert opm.io.Parser().parse_string(vfpstr, parsecontext)

    # Call eclcompress as script on vfpstr:
    with open("vfpfile.inc", "w") as testdeck:
        testdeck.write(vfpstr)
    print("foo")
    sys.argv = ["eclcompress", "--keeporiginal", "vfpfile.inc"]  # noqa
    eclc.main()

    # Check that OPM can parse the output (but in this case, OPM allows
    # having the slashes on the next line, so it is not a good test)
    assert opm.io.Parser().parse_string(open("vfpfile.inc").read(), parsecontext)

    # Verify that a slash at record-end is still there. This test will pass
    # whether eclcompress is just skipping the file, or of it is able to
    # compress it correctly.
    assert "8000 10000 /" in open("vfpfile.inc").read()


def test_main():
    """Test installed endpoint"""

    testdir = os.path.join(os.path.dirname(__file__), "testdata_eclcompress")
    if not os.path.exists(testdir):
        os.mkdir(testdir)
    os.chdir(testdir)

    with open("testdeck.inc", "w") as testdeck:
        for line in FILELINES:
            testdeck.write(line + "\n")

    if os.path.exists("testdeck.inc.orig"):
        os.unlink("testdeck.inc.orig")

    sys.argv = ["eclcompress", "--keeporiginal", "testdeck.inc"]  # noqa
    eclc.main()

    assert os.path.exists("testdeck.inc.orig")
    assert os.path.exists("testdeck.inc")
    compressedlines = open("testdeck.inc").readlines()
    compressedbytes = sum([len(x) for x in compressedlines if not x.startswith("--")])
    origbytes = sum([len(x) for x in FILELINES])

    assert compressedbytes < origbytes

    compressedstr = "\n".join(compressedlines)
    parsecontext = opm.io.ParseContext(
        [("PARSE_MISSING_DIMS_KEYWORD", opm.io.action.ignore)]
    )
    assert opm.io.Parser().parse_string(compressedstr, parsecontext)
