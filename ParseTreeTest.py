"""
Testing module for Parser.py
"""

from Parser import Parser
from ParseTree import *

# A test version of Enumerator, which just hard-codes some groups for
#   testing the functionality of Parser.parse().
#
class TestEnumerator:
    def list_emails(self, group):
        # hard-coded dictionary of group -> members
        groups = {
                'A': ['a1', 'a2', 'a3', 'a4', 'a5'],
                'B': ['b1', 'b2', 'b3'],
                'C': ['c1', 'c2', 'c3', 'c4'],
                }

        return {'result':groups[group] if group in groups else [group]}

# Run the test suite
def run_tests():
    # hard-coded list of sample query, expected result
    tests = [
            (Expr(EmailSet('A'),UnionOp,EmailSet('B')), ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3']),
            (Expr(EmailSet('A'),DiffOp,EmailSet('a2')), ['a1', 'a3', 'a4', 'a5']),
            (Expr(Expr(EmailSet('A'),UnionOp,EmailSet('B')),
                DiffOp,EmailSet('b1')), ['a1','a2','a3','a4','a5','b2','b3']),
            (Expr(Expr(EmailSet('A'),UnionOp,EmailSet('B')), UnionOp,
                EmailSet('C')) ,['a1','a2','a3','a4','a5','b1','b2','b3','c1',
                'c2','c3','c4']),
            (Expr(Expr(EmailSet('A'),UnionOp,EmailSet('b1')),IntersectOp,EmailSet('B')),
                ['b1']),
            (Expr(Expr(Expr(EmailSet('B'),UnionOp,EmailSet('kyc2915')),
                UnionOp,EmailSet('trzhang')),DiffOp,EmailSet('kyc2915')),
                ['b1','b2','b3','trzhang']),
            (Expr(EmailSet('A'),DiffOp,Expr(EmailSet('B'),UnionOp,EmailSet('a1'))),
                ['a2', 'a3', 'a4','a5']),
            (Expr(Expr(Expr(EmailSet('A'),UnionOp,EmailSet('c1')),UnionOp,EmailSet('B')),
                SymDiffOp,Expr(EmailSet('C'),UnionOp,EmailSet('a1'))),
                ['a2','a3','a4','a5','b1','b2','b3','c2','c3','c4']),
            ]

    enumerator = TestEnumerator()

    num_failures = 0
    for query, expected in tests:
        result = query.eval(enumerator)
        print 'testing ' + str(query) + '...'
        if 'error' in result:
            if 'error' in expected:
                print 'Found expected error: %s' % result['error']
            else:
                num_failures += 1
                print 'ERROR: %s' % result['error']
        elif 'result' not in result:
            num_failures += 1
            print 'ERROR: returned dictionary missing result'
        elif set(result['result']) != set(expected):
            num_failures += 1
            print 'ERROR: got', result, 'but expected', expected

    print 'Ran', len(tests), 'tests, got', num_failures, 'failures'


if __name__ == '__main__':
    run_tests()
