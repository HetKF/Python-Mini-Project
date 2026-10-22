# The AI part: a small linear regression that predicts battery temperature from cooling settings


class LinearModel:
    def __init__(self):
        self.w = None
        self.r2 = None
        self.n = 0

    @staticmethod
    def _solve(A, b):
        n = len(A)
        M = [row[:] + [b[i]] for i, row in enumerate(A)]
        for i in range(n):
            p = max(range(i, n), key=lambda r: abs(M[r][i]))
            M[i], M[p] = M[p], M[i]
            if abs(M[i][i]) < 1e-12:
                raise ValueError("Singular matrix - need more varied data")
            for r in range(i + 1, n):
                f = M[r][i] / M[i][i]
                for c in range(i, n + 1):
                    M[r][c] -= f * M[i][c]
        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
        return x

    def fit(self, rows):
        X = [[1.0, r["reynolds"], r["concentration"], r["inlet_temp"]] for r in rows]
        y = [r["max_temp"] for r in rows]
        if len(X) < 5:
            raise ValueError("Need at least 5 CFD runs to train")
        k = len(X[0])
        XtX = [[sum(x[i] * x[j] for x in X) for j in range(k)] for i in range(k)]
        Xty = [sum(x[i] * yi for x, yi in zip(X, y)) for i in range(k)]
        self.w = self._solve(XtX, Xty)
        mean = sum(y) / len(y)
        ss_tot = sum((v - mean) ** 2 for v in y)
        ss_res = sum((yi - self.predict(x[1], x[2], x[3])) ** 2 for x, yi in zip(X, y))
        self.r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
        self.n = len(X)

    def predict(self, reynolds, conc, inlet):
        if self.w is None:
            raise ValueError("Model not trained")
        return self.w[0] + self.w[1] * reynolds + self.w[2] * conc + self.w[3] * inlet
