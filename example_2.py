from main import Formula

p = Formula("p")
q = Formula("q")
r = Formula("r")

main = ((p.implies(r)).not_()).implies(q.not_())
a = q.implies(p.implies(r))
b = (p.implies(r)).and_(q.not_())
c = (p.implies(r)).or_(q)
d =  (p.implies(r)).or_(q.not_())
e = (q.not_()).implies((p.implies(r)).not_())

print(main.is_equivalent(a))
print(main.is_equivalent(b))
print(main.is_equivalent(c))
print(main.is_equivalent(d))
print(main.is_equivalent(e))