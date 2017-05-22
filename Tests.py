"""
Contains full tests for the entire system, except for sending.
"""

from Enumerator import Enumerator
from Parser import Parser
from Screener import Screener
from Processor import Processor
import Messages

tests = [
        # basic functionality
        (['mbt-moira--michaelx@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu', 'beckyshi@mit.edu']}),
        (['{mbt-moira}-{michaelx}@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu', 'beckyshi@mit.edu']}),

        # subtract lists
        (['{mkbt}-{mbt-moira}@simple.mit.edu'],
            {'sent-to': ['kyc2915@mit.edu']}),

        # parse errors
        (['-{michaelx}@simple.mit.edu'],
            {'message': Messages.MISSING_GROUP_PARSE_ERROR}),
        (['{michaelx}-@simple.mit.edu'],
            {'message': Messages.MISSING_GROUP_PARSE_ERROR}),
        (['{next-forum}---{michaelx}@simple.mit.edu'],
            {'message': Messages.MISSING_GROUP_PARSE_ERROR}),
        (['{next-forum}-+{michaelx}@simple.mit.edu'],
            {'message': Messages.MISSING_GROUP_PARSE_ERROR}),
        (['{mbt-moira}--{michaelx}@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu', 'beckyshi@mit.edu']}),
        (['{mbt-moira}--michaelx@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu', 'beckyshi@mit.edu']}),
        (['{mbt-moira}--michaelx--beckyshi@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu']}),
        (['{mbt-moira}--michaelx-{beckyshi}@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu']}),
        (['{mbt-moira}-{michaelx}-{beckyshi}@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu']}),
        (['{mbt-moira}-{trzhang++beckyshi}@simple.mit.edu'],
            {'sent-to': ['michaelx@mit.edu']}),
        (['{mbt-moira-many-hyphens++michaelx++beckyshi}-michaelx-{beckyshi}--trzhang@simple.mit.edu'],
            {'sent-to': ['kyc2915@mit.edu']}),
        (['mbt-moira-many-hyphens-{michaelx}--{beckyshi}-{trzhang}@simple.mit.edu'],
            {'sent-to': ['kyc2915@mit.edu']}),
        (['mbt-moira-many-hyphens-{michaelx}--beckyshi-{trzhang}@simple.mit.edu'],
            {'sent-to': ['kyc2915@mit.edu']}),
        (['@simple.mit.edu'],
            {'message': Messages.MISSING_GROUP_PARSE_ERROR}),
        (['-@simple.mit.edu'],
            {'message': Messages.INVALID_TOKEN_PARSE_ERROR % '-'}),
        (['--@simple.mit.edu'],
            {'message': Messages.MISSING_GROUP_PARSE_ERROR}),
        (['{next-forum}{next}@simple.mit.edu'],
            {'message': Messages.MISSING_OPERATOR_PARSE_ERROR}),
        (['{next-forum}${next}@simple.mit.edu'],
            {'message': Messages.MISSING_OPERATOR_PARSE_ERROR}),
        (['{mbt-moira}-{michaelx++trzhang@simple.mit.edu'],
            {'sent-to': ['beckyshi@mit.edu']}),

        # empty subtract error
        (['mbt-moira--kyc2915@simple.mit.edu'],
            {'message': Messages.NONFUNCTIONING_SUBTRACT_ERROR}),

        # mailman group
        (['{next}@simple.mit.edu'],
            {'message': Messages.MAILMAN_ERROR % 'next'}),
        (['{next}-{kyc2915}@simple.mit.edu'],
            {'message': Messages.MAILMAN_ERROR % 'next'}),
        (['{next}-{runbobby}@simple.mit.edu'],
            {'message': Messages.MAILMAN_ERROR % 'next'}),

        # top-level warnings vs. lower-level no warnings
        (['{itsdchen}@simple.mit.edu'],
            {'message': Messages.PRIVATE_GROUP_ERROR % ('itsdchen', 'link')}),
        (['{mkbt}@simple.mit.edu'],
            {'sent-to': ['michaelx@mit.edu', 'kyc2915@mit.edu', 'beckyshi@mit.edu', 'trzhang@mit.edu']}),

        # nonexistent kerberos/lists
        (['somethingnonexistent@simple.mit.edu'],
            {'message': Messages.INVALID_GROUP_ERROR % 'somethingnonexistent'}),
        (['safetythird-natalle@simple.mit.edu'],
            {'message': Messages.INVALID_GROUP_ERROR % 'safetythird-natalle'}),

        # private lists override null intersection
        (['safetythird--3wsecretsanta2013@simple.mit.edu'],
            {'message': Messages.PRIVATE_GROUP_ERROR % ('3wsecretsanta2013', 'link')}),
        (['3wsecretsanta2013-minus-kyc2915@simple.mit.edu'],
            {'message': Messages.PRIVATE_GROUP_ERROR % ('3wsecretsanta2013', 'link')}),

        # test that phulin, a KERBEROS: email, will not be used
        (['next-forum-intersect-phulin@simple.mit.edu'],
            {'sent-to': []}),

        # multiple recipients
        (['kyc2915@mit.edu', 'mbt-moira--michaelx@simple.mit.edu'],
            {'sent-to': ['trzhang@mit.edu', 'beckyshi@mit.edu']}),
        (['mkbt-minus-beckyshi@simple.mit.edu', 'mkbt-minus-trzhang@simple.mit.edu'],
            {'sent-to': ['michaelx@mit.edu', 'beckyshi@mit.edu', 'kyc2915@mit.edu']}),

        # dry runs
        (['mbt-moira--michaelx.dryrun@simple.mit.edu'],
            {'message': """Take the list mbt-moira, subtract the user michaelx, and send.

Some emails that your message will be sent to: beckyshi@mit.edu, trzhang@mit.edu
Some emails that your message will NOT be sent to: michaelx@mit.edu"""}),
        (['mbt-moira--kyc2915.dryrun@simple.mit.edu'],
            {'message': Messages.NONFUNCTIONING_SUBTRACT_ERROR}),
        (['-{michaelx}.dryrun@simple.mit.edu'],
            {'message': Messages.MISSING_GROUP_PARSE_ERROR}),

        # special emails
        (['admin@simple.mit.edu'],
            {'sent-to': ['next-code-admin@mit.edu']}),
        (['root@simple.mit.edu'],
            {}),
        ]

test_result = None  # set to the results of each test
tests = []
class TestSender:
    def redirect(self, sentto, data):
        global test_result
        assert data == 'message'
        test_result = {'sent-to': sentto}
        return {}

    def send(self, mailfrom, rcptto, subject, message):
        global test_result
        assert mailfrom == 'admin@simple.mit.edu'
        assert rcptto == 'mailfrom'
        test_result = {'message': message}
        return {}


# Run the test suite
def run_tests():
    global test_result
    TEST_ENV = {
            'stopped': False,
            'test': True,
            'send': False,
            }

    TEST_ENV['sender'] = TestSender()
    TEST_ENV['enumerator'] = Enumerator(TEST_ENV)
    TEST_ENV['parser'] = Parser(TEST_ENV)
    TEST_ENV['screener'] = Screener(TEST_ENV)
    TEST_ENV['logger'] = open('/dev/null', 'w')
    TEST_ENV['processor'] = processor = Processor(TEST_ENV)

    num_failures = 0
    for (rcpttos, expected) in tests:
        test_result = {}
        processor.process_message({
            'peer': None,
            'mailfrom': 'mailfrom',
            'rcpttos': rcpttos,
            'data': 'message',
            })
        print 'testing sending to', rcpttos, '...'
        for key in expected:
            assert key in test_result
            if type(test_result[key]) == type([]):
                assert set(test_result[key]) == set(expected[key])
            else:
                assert test_result[key] == expected[key]
        for key in test_result:
            assert key in expected


print 'Running enumerator tests...'
import EnumeratorTest
EnumeratorTest.run_tests()

print 'Running parser tests...'
import ParserTest
ParserTest.run_tests()

print 'Running parse tree tests...'
import ParseTreeTest
ParseTreeTest.run_tests()

print 'Running system tests...'
run_tests()
