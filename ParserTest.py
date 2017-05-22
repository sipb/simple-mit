"""
Testing module for Parser.py
"""

from Parser import Parser

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
                'D': ['d1', 'd2', 'd7'],
                '-C': ['c1', 'c2', 'c3'],
                'C-': ['c1', 'c2', 'c3'],
                '+C': ['c1', 'c2', 'c4'],
                'C+': ['c1', 'c2', 'c4'],
                }

        return {'result':groups[group] if group in groups else [group]}

# Run the test suite
def run_tests():
    # hard-coded list of sample query, expected result
    tests = [
            ('{A}+{B}', ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3']),
            ('{A}-{a2}', ['a1', 'a3', 'a4', 'a5']),
            ('{A}+{B}-{b1}', ['a1','a2','a3','a4','a5','b2','b3']),
            ('{A}+{C}+{B}',['a1','a2','a3','a4','a5','b1','b2','b3','c1',
                'c2','c3','c4']),
            ('{B}+{kyc2915}+{trzhang}-{kyc2915}',['b1','b2','b3','trzhang']),
            ('{A}+{b1}&{B}',['b1']),
            ('{A}+{B}+{C}-{c1}&{C}',['c2','c3','c4']),
            ('{A}-{C}',['a1', 'a2', 'a3', 'a4', 'a5']),
            ('{B}+{c1}-{C}',['b1','b2','b3']),
            ('-{B}+{C}',{'error': 'Missing initial set'}),
            ('{A}++{B}', ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3']),
            ('{A}{}+{B}',['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3']),
            ('{{A}+{B}}',['a1','a2','a3','a4','a5','b1','b2','b3']),
            ('{next-forum}+{B}',['next-forum','b1','b2','b3']),
            ('{next+forum}+{B}',['next+forum','b1','b2','b3']),
            ('{{A}+{b1}}^{B}', ['a1','a2','a3','a4','a5','b2','b3']),
            ('{A}-{{A}-{a1}}', ['a1']),
            ('{{{B}+{{C}-{{c1}+{c2}}}}-{{B}-{{b1}&{B}}}}', ['b1','c3','c4']),
            ('{{A}+{b1}}^{B}', ['a1','a2','a3','a4','a5','b2','b3']),
            ('A++B', ['a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3']),
            ('A--a2', ['a1', 'a3', 'a4', 'a5']),
            ('A++B--b1', ['a1','a2','a3','a4','a5','b2','b3']),
            ('A++C++B',['a1','a2','a3','a4','a5','b1','b2','b3','c1',
                'c2','c3','c4']),
            ('B++kyc2915++trzhang--kyc2915',['b1','b2','b3','trzhang']),
            ('A++b1&&B',['b1']),
            ('A++B++C--c1&&C',['c2','c3','c4']),
            ('A--C',['a1', 'a2', 'a3', 'a4', 'a5']),
            ('A--a2', ['a1', 'a3', 'a4', 'a5']),
            ('A++B--b1', ['a1','a2','a3','a4','a5','b2','b3']),
            ('A-minus-a2', ['a1', 'a3', 'a4', 'a5']),
            ('A-plus-B-minus-b1', ['a1','a2','a3','a4','a5','b2','b3']),
            ('A++B-{b1}', ['a1','a2','a3','a4','a5','b2','b3']),
            ('{A-plus-B}-minus-b1', ['a1','a2','a3','a4','a5','b2','b3']),
            ('{A-plus-B-minus-b1}', ['a1','a2','a3','a4','a5','b2','b3']),
            ('{A-plus-B-minus-b1}++{{b1++b2}-b1}', ['a1','a2','a3','a4','a5','b2','b3']),
            ('{-C++b1}', ['c1', 'c2', 'c3', 'b1']),
            ('{b1++-C}', ['c1', 'c2', 'c3', 'b1']),
            ('{{{b1++b2}++b3}++-C}', ['c1', 'c2', 'c3', 'b1', 'b2', 'b3']),
            ('{{{B--b2}-minus-b3}++-C}', ['c1', 'c2', 'c3', 'b1']),
            ('{{{B--b2&&b2}-minus-b3}++-C}', ['c1', 'c2', 'c3']),
            ('{{B&&{b2++b4}-plus-b3}-{b3++b4}}++C-', ['c1', 'c2', 'c3', 'b2']),
            ('{+C++b1}', ['c1', 'c2', 'c4', 'b1']),
            ('{b1+++C}', ['c1', 'c2', 'c4', 'b1']),
            ('-C-intersect-{b1+++C}', ['c1', 'c2']),
            ('-C-intersect--C', ['c1', 'c2', 'c3']),
            ('C-intersect--C', ['c1', 'c2', 'c3']),
            ('{A-plus-B-minus-b1}', ['a1','a2','a3','a4','a5','b2','b3']),
            ('{A-plus-B-minus-b1++-C}', ['a1','a2','a3','a4','a5','b2','b3', 'c1', 'c2', 'c3']),
            ('-C++A-plus-B-minus-{b1}', ['a1','a2','a3','a4','a5','b2','b3', 'c1', 'c2', 'c3']),
            ('-C^^C-+{b1}', ['b1']),
            ('{-C&&C}&C-+{b1}', ['c1','c2','c3','b1']),
            ('{-C&&C}&c1+{b1}', ['c1','b1']),
            ('{C-++C^^-C}&c1+{b1}', ['b1']),
            ('{{C-}+C^^{-C}}&c4+{b1}', ['b1','c4']),
            ('{{C-}+C---C}&c4+{b1}-plus-b2', ['b1','c4','b2']),
            ('{{C-}+C&&-C}&c4+{b1}-plus-b2', ['b1','b2']),
            ('{{C-}+C&&-C}&c4+{b1}-plus--C', ['b1','c1','c2','c3']),
            ('{{C+}+C&&-C}&c4+{b1}-plus--C', ['b1','c1','c2','c3']),
            ('{{C+}++C---C}&c4+{b1}-plus-+C', ['b1','c1','c2','c4']),
            ('{{C+}++C---C}&c4+{{b1}-plus-+C++d1-plus-d2&&{D}}', ['c4','d1','d2']),
            ('{{C+}++C---C}&c4+{{b1}+d1-plus-d2++{D}}', ['c4','d1','d2','d7','b1']),
            ('a-at-mit.edu', ['a@mit.edu']),
            ('{a-at-mit.edu}+{b-at-mit.edu}', ['a@mit.edu', 'b@mit.edu']),
            ('a.b-at-mit.edu', ['a.b@mit.edu']),
            ('a-at-b', ['a-at-b']),
            ]

    parser = Parser({'enumerator': TestEnumerator()})

    num_failures = 0
    for query, expected in tests:
        result = parser.parse(query, {})
        print 'testing ' + query + '...'
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
