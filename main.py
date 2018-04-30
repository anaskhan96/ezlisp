import math
import operator as op

Symbol = str
Number = (int, float)
Atom = (Symbol, Number)
List = list
Exp = (Atom, List)
Env = dict

class Env(dict):
	def __init__(self, parms=(), args=(), outer=None):
		self.update(zip(parms, args))
		self.outer = outer
	def find(self, var):
		return self if (var in self) else self.outer.find(var)

class Procedure(object):
	def __init__(self, parms, body, env):
		self.parms, self.body, self.env = parms, body, env
	def __call__(self, *args): 
		return eval(self.body, Env(self.parms, args, self.env))

def stdenv():
	env = Env()
	env.update(vars(math))
	env.update({
		'+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'modulo':  op.mod,
        'abs':     abs,
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'expt':    pow,
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: List(x), 
        'list?':   lambda x: isinstance(x, List), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),  
		'print':   print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),	
	})
	return env

global_env = stdenv()

def tokenize(chars):
	return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(src):
	return match_tokens(src)

def match_tokens(tokens):
	if len(tokens) == 0:
		raise SyntaxError('EOF already?')
	token = tokens.pop(0)
	if token == '(':
		l = []
		while tokens[0] != ')':
			l.append(match_tokens(tokens))
		tokens.pop(0)
		return l
	elif token == ')':
		raise SyntaxError('not a valid expression')
	else:
		return atomise(token)

def atomise(token):
	try:
		return int(token)
	except ValueError:
		try:
			return float(token)
		except ValueError:
			return Symbol(token)

def eval(x, env=global_env):
	if isinstance(x, Symbol): 
		return env.find(x)[x]
	elif not isinstance(x, List):
		return x   
	op, *args = x
	if op == 'quote':
		return args[0]
	elif op == 'if':
		(cond, conseq, alt) = args
		exp = (conseq if eval(cond, env) else alt)
		return eval(exp, env)
	elif op == 'define':
		(symbol, exp) = args
		env[symbol] = eval(exp, env)
	elif op == 'set!':
		(symbol, exp) = args
		env.find(symbol)[symbol] = eval(exp)
	elif op == 'lambda':
		(parms, body) = args
		return Procedure(parms, body, env)
	else:
		proc = eval(op, env)
		vals = [eval(arg, env) for arg in args]
		return proc(*vals)

while True:
	res = eval(parse(tokenize(input("ezlisp > "))))
	if res != None:
		print(res)