from main import Formula

p = Formula("p")
q = Formula("q")
r = Formula("r")
s = Formula("s")

f = (p.implies((q.not_()).or_(s))).and_((s.not_()).implies(r))
print(f)

table = f.table()
print(table)

print(f.eval(p=1, q=0, r=1, s=1)) # will print a bool