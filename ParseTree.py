import re
import Messages

idPattern = re.compile('(\$\d+)')

SAMPLE_SIZE = 5

# Operation
class Op:

    @classmethod
    def operate(cls, setA, setB):
        if type(setA) != set or type(setB) != set:
            return None
        return cls.op(setA, setB)

class IntersectOp(Op):

    @staticmethod
    def op(x,y):
        return {'result':x.intersection(y)}

class UnionOp(Op):
    
    @staticmethod
    def op(x,y):
        return {'result':x.union(y)}

class SymDiffOp(Op):

    @staticmethod
    def op(x,y):
        return {'result':x.symmetric_difference(y)}

class DiffOp(Op):

    @staticmethod
    def op(x,y):
        warnings = []
        if not x.intersection(y):
            warnings.append(('NONFUNCTIONING_SUBTRACT',))
        return {'result': x.difference(y), 'warnings': warnings}

opDict = {'+': UnionOp, '-': DiffOp, '^': SymDiffOp, '&': IntersectOp}
descriptionDict = {UnionOp: 'add', DiffOp: 'subtract', SymDiffOp: 'xor', IntersectOp: 'intersect'}

# General expression class
#
# Only requirement is an eval method, returns standard
# dictionary, with type(result) = set
class Expr:

    def __init__(self, exprA, operator, exprB):
        self.left = exprA
        self.leftSet = None
        self.right = exprB
        self.rightSet = None
        self.operator = operator
        self.value = None

    def eval(self, enumerator):
        if self.value and ('error' not in self.value):
            return self.value

        warnings = []

        if not self.leftSet:
            exprData = self.left.eval(enumerator)
            if 'error' in exprData:
                self.value = {'error' : exprData['error']}
                return self.value
            self.leftSet = exprData['result']

            warnings.extend(exprData['warnings'] if 'warnings'
                    in exprData else [])

        if not self.rightSet:
            exprData = self.right.eval(enumerator)
            if 'error' in exprData:
                self.value = {'error' : exprData['error']}
                return self.value
            self.rightSet = exprData['result']

            warnings.extend(exprData['warnings'] if 'warnings'
                    in exprData else [])

        evaluated = self.operator.operate(self.leftSet, self.rightSet)
        if 'error' in evaluated:
            return {'error': evaluated['error']}
        if 'warnings' in evaluated:
            warnings.extend(evaluated['warnings'])

        self.value = {'result': evaluated['result']}

        if len(warnings):
            self.value['warnings'] = warnings
        return self.value

    # Returns a description of the evaluation of the parse tree
    def description(self, flags):
        description = self.description_help(flags)
        if 'mit_only' in flags and flags['mit_only']:
            description += "filter only for '@mit.edu' addresses, "
        description += 'and send.'
        index = ord('A')  # for unique letter identifiers
        while True:
            idMatcher = idPattern.search(description)
            if not idMatcher:
                return {'result': description}
            description = description.replace(idMatcher.group(0), chr(index))
            index += 1
            if index > ord('Z'):  # shouldn't happen if string length is capped
                return {'error': Messages.SYSTEM_ERROR}

    # Helper function for description()
    def description_help(self, flags):
        if self.left.__class__ == EmailSet:
            if self.right.__class__ == EmailSet:
                return 'Take %s, %s %s, ' \
                        % (self.left.__str__(), descriptionDict[self.operator], self.right.__str__())
            else:
                return (self.right.description_help(flags) + \
                        'call that $%d. Take %s, %s $%d, ') \
                        % (id(self.right), self.left.__str__(), descriptionDict[self.operator], id(self.right))
        else:
            if self.right.__class__ == EmailSet:
                return (self.left.description_help(flags) + \
                        '%s %s, ') % (descriptionDict[self.operator], self.right.__str__())
            else:
                return (self.left.description_help(flags) + \
                        'call that $%d. ' + \
                        self.right.description_help(flags) + \
                        'call that $%d. Take $%d, %s $%d, ') \
                        % (id(self.left), id(self.right), id(self.left), descriptionDict[self.operator], id(self.right))

    # Get set of sample emails in this subtree
    def get_samples(self, flags):
        reps = self.left.get_samples(flags)
        reps = reps.union(self.right.get_samples(flags))
        return reps

    def __str__(self):
        return '{%s %s %s}' % (str(self.left),str(self.operator),str(self.right))

# This class represents an email set, terminal expression
class EmailSet(Expr):

    def __init__(self, name):
        self.name = name
        self.result = None
    
    def getName(self):
        return self.name

    def eval(self, enumerator):
        # No need to retry if there were no errors
        if self.result and ('error' not in self.result):
            return self.result

        warnings, resultSet = [], set()
        listEmailsResult = enumerator.list_emails(self.name)

        if 'error' in listEmailsResult:
            self.result = {'error': listEmailsResult['error']}
            return self.result
        warnings.extend(listEmailsResult['warnings']
                if 'warnings' in listEmailsResult else [])

        resultSet = set(listEmailsResult['result'])

        self.result = {'result' : resultSet, 'warnings' : warnings}
        return self.result

    def description(self, flags):
        des = self.description_help(flags)
        if 'mit_only' in flags and flags['mit_only']:
            des += "filter only for '@mit.edu' addresses, "
        return {'result': des + 'and send.'}

    def description_help(self, flags):
        return 'Take %s, ' % self.__str__()

    def get_samples(self, flags):
        if self.result and ('error' not in self.result):
            reps = self.result['result']
            if len(reps) > SAMPLE_SIZE:
                return set(list(reps)[:SAMPLE_SIZE])
            else:
                return reps
        return set()

    def __str__(self):
        if self.result and ('error' not in self.result):  # more descriptive string
            if len(self.result['result']) == 1 and list(self.result['result'])[0] == self.name + '@mit.edu':  # hacky way of determining if this is a user
                return 'the user %s' % str(self.name)
            else:
                return 'the list %s' % str(self.name)
        return '%s' % str(self.name)
