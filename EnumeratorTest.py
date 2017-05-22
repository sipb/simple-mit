"""
Testing module for Enumerator.py
"""

from Enumerator import Enumerator

# Run the test suite
def run_tests():
    TEST_ENV = {
            'test': True,
            }
    enumerator = Enumerator(TEST_ENV)

    # hard-coded list of sample query, expected result
    tests = [
            ('michaelx', ['michaelx@mit.edu']),
            ('michaeljxu@gmail.com', ['michaeljxu@gmail.com']),
            ('next-code-admin', ['kyc2915@mit.edu', 'michaelx@mit.edu']),
            ('Next-Code-Admin', ['kyc2915@mit.edu', 'michaelx@mit.edu'])
            ]

    num_failures = 0
    for query, expected in tests:
        result = enumerator.list_emails(query)['result']
        print 'testing ' + query + '...'
        if set(result) != set(expected):
            num_failures += 1
            print 'ERROR: got', result, 'but expected', expected

    print 'Ran', len(tests), 'tests, got', num_failures, 'failures'


if __name__ == '__main__':
    run_tests()
