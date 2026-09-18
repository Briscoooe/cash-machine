import math
n=56; elapsed=38.4; total=48
lam = n/elapsed*(total-elapsed)
from math import exp, factorial
for cap,label in ((39,'<40'),(64,'<=64'),(89,'<=89')):
    if cap>=n:
        p=sum(exp(-lam)*lam**k/factorial(k) for k in range(cap-n+1))
        mu=n+lam; sd=math.sqrt(2*lam)
        pn=0.5*(1+math.erf((cap+0.5-mu)/(sd*math.sqrt(2))))
    else:
        p=pn=0.0
    print("%s: Poisson %.3f overdisp %.3f" % (label,p,pn))
print("40-64 band = P(<=64)-P(<40) under both")
