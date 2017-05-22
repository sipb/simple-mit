"""
Parser.py

Parses an expression sent as the recipient to simple.mit.edu.
"""

import re
import Messages, ParseTree

## Braces Spec
# --, ++, ^^, &&, -minus-, -plus, -intersect- are always operators
# -, +, ^, & are assumed to be part of a mailing list unless outwardly adjacent to a brace
# ex: }-, -{, but not -}, {-
##
operatorString = '(\+\+)|(--)|(\^\^)|(&&)|(-minus-)|(-plus-)|(-intersect-)'
impendingOp = operatorString + '|([-^&+]{)|(}[-^&+])'
# Matches everything except {} up to the next operator - much more general email set matching
setPattern = re.compile(r'(?:(?!(impendingOp))[^{}])+'.replace('impendingOp', impendingOp))
# Implements operator spec above, two extra cases for }-, -{
opPattern = re.compile(r'(operatorString|((?<=})[+&^-])|([+&^-](?={)))'.replace('operatorString', operatorString))
quick_ops = {'--': '-', '++': '+', '&&': '&',
        '-minus-': '-', '-plus-': '+', '-intersect-': '&'}

emailPattern = re.compile(r'.+-at-.+\..+')
def parse_set_pattern(expr):
    # Convert special syntax tokens to proper characters
    if emailPattern.match(expr):
        return expr.replace('-at-', '@')
    else:
        return expr

# Method 1: parse expr of form '{safetythird}-{michaelx}'
# Returns a list of tokens (type, val)
def expr_to_RPN(expr):
    # Using the Shunting Yard Algorithm
    stack, output, index = [],[],0

    while index < len(expr):
        setMatcher = setPattern.match(expr, index)
        opMatcher = opPattern.match(expr, index)

        if expr[index] == '{':
            stack.append(('lparen','{'))
            index += 1
        elif expr[index] == '}':
            while stack and stack[-1][0] != 'lparen':
                output.append(stack.pop())
            # if the stack is empty, braces are mismatched
            if not stack:
                return {'error':  Messages.MISMATCHED_BRACES_PARSE_ERROR}
            stack.pop()
            index += 1
        elif opMatcher:
            opString = opMatcher.group()
            opKey = opMatcher.group()[0]
            if len(opString) > 2:
                if 'minus' in opString:
                    opKey = '-'
                if 'plus' in opString:
                    opKey = '+'
                if 'intersect' in opString:
                    opKey = '&'
            while stack and stack[-1][0] == 'op':
                output.append(stack.pop())
            stack.append(('op', opKey))
            index = opMatcher.end()
        elif setMatcher:
            output.append(('set', parse_set_pattern(setMatcher.group(0))))
            index = setMatcher.end()
        else:
            return {'error': Messages.INVALID_TOKEN_PARSE_ERROR % expr[index:]}

    # pop stack to output
    while stack:
        output.append(stack.pop())

    return {'result' : output}

# Convert a list of tokens in RPN format to a tree.
def toAST(rpn):
    stack = []
    for val in rpn:
        if val[0] == 'set':
            stack.append(ParseTree.EmailSet(val[1]))
        elif val[0] == 'op':
            if len(stack) < 2:
                return {'error' : Messages.MISSING_GROUP_PARSE_ERROR}

            right = stack.pop()
            left = stack.pop()

            if val[1] not in ParseTree.opDict:
                return {'error' : Messages.INVALID_OPERATOR_PARSE_ERROR % val[1]}

            stack.append(ParseTree.Expr(left, ParseTree.opDict[val[1]], right))

    if len(stack) == 0:
        return {'error': Messages.MISSING_GROUP_PARSE_ERROR}
    elif len(stack) >= 2:
        return {'error': Messages.MISSING_OPERATOR_PARSE_ERROR}

    return {'result': stack[0]}

# Give sample emails that the message will be sent/not sent to.
# emails is a collection of emails that the message will be sent to.
def displaySamples(samples, emails, flags):
    if 'mit_only' in flags and flags['mit_only']:
        mitonly_emails = filter(lambda email: '@mit' in email.lower(), list(emails))
        emails = mitonly_emails
    return ('Some emails that your message will be sent to: %s\n' + \
            'Some emails that your message will NOT be sent to: %s') % \
            (', '.join(list(emails)[:ParseTree.SAMPLE_SIZE]), \
            ', '.join(filter(lambda email: email not in emails, samples)[:ParseTree.SAMPLE_SIZE]))


class Parser:

    def __init__(self, ENV):
        self.ENV = ENV

    # Parses the given expression and returns a result dictionary
    # e.g. parse('{next}-{mjx}@simple.mit.edu') returns
    # {
    #   result: [tommy@mit.edu, becky@mit.edu, ...]
    #   dryrun: [some text]
    # }
    def parse(self, expr, flags):
        rpn = expr_to_RPN(expr)
        warnings = []

        if 'error' in rpn:
            return {'error': rpn['error']}
        warnings.extend(rpn['warnings'] if 'warnings' in rpn else [])

        ast = toAST(rpn['result'])

        if 'error' in ast:
            return {'error': ast['error']}
        warnings.extend(ast['warnings'] if 'warnings' in ast else [])

        evaluated = ast['result'].eval(self.ENV['enumerator'])

        data = dict()

        if 'error' in evaluated:
            return {'error': evaluated['error']}
        warnings.extend(evaluated['warnings'] if 'warnings' in evaluated else [])

        description = ast['result'].description(flags)
        if 'error' in description:
            return {'error': description['error']}
        warnings.extend(description['warnings'] if 'warnings' in description else [])

        data['dryrun'] = description['result'] + '\n\n' + \
                displaySamples(ast['result'].get_samples(flags), evaluated['result'], flags)
        data['result'] = list(evaluated['result'])

        if warnings:
            data['warnings'] = warnings

        return data


