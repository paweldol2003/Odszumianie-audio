r = 4
lam = 0.999
okno = 221

a = np.zeros(r)
P = 1000 * np.eye(r)
z = x.copy()  # historia do predykcji
e = np.full(len(x), np.nan)
prog = np.full(len(x), np.nan)
maska = np.zeros(len(x), dtype=bool)
a_hist = np.full((len(x), r), np.nan)

for k in range(r, len(x)):
    phi = z[k-r:k][::-1]
    predykcja = a @ phi
    e[k] = x[k] - predykcja
    if k >= r + okno:
        prog[k] = 3 * np.std(e[k-okno:k])
        maska[k] = abs(e[k]) > prog[k]

    if maska[k]:
        z[k] = z[k-1]
        P = P / lam
    else:
        q = P @ phi
        g = q / (lam + phi @ q)
        a = a + g * e[k]
        P = (P - np.outer(g, phi @ P)) / lam
    a_hist[k] = a
