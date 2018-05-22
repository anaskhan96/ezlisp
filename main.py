from env import *

global_env = stdenv()

class Procedure(object):
	def __init__(self, parms, body, env):
		self.parms, self.body, self.env = parms, body, env
	def __call__(self, *args): 
		return evaluate(self.body, Env(self.parms, args, self.env))

def tokenize(src):
	return src.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(tokens):
	return match_tokens(tokens)

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

def evaluate(x, env=global_env):
	if isinstance(x, Symbol): 
		return env.find(x)[x]
	elif not isinstance(x, List):
		return x   
	op, *args = x
	if op == 'quote':
		return args[0]
	elif op == 'if':
		(cond, conseq, alt) = args
		exp = (conseq if evaluate(cond, env) else alt)
		return evaluate(exp, env)
	elif op == 'define':
		(symbol, exp) = args
		env[symbol] = evaluate(exp, env)
	elif op == 'set!':
		(symbol, exp) = args
		env.find(symbol)[symbol] = evaluate(exp)
	elif op == 'lambda':
		(parms, body) = args
		return Procedure(parms, body, env)
	else:
		proc = evaluate(op, env)
		vals = [evaluate(arg, env) for arg in args]
		return proc(*vals)

while True:
	src = input("ezlisp > ")
	if src == 'exit':
		exit(0)
	res = evaluate(parse(tokenize(src)))
	if res != None:
		print(res)