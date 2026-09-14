import ast
import time
from typing import Tuple, Optional, Set, Any
import sympy as sp
from app.cas.preprocessor import ImplicitMultiplicationPreprocessor


class SecurityViolationError(Exception):
    """AST güvenlik ihlali durumunda fırlatılır."""
    pass


class SymbolicEquivalenceEngine:
    """
    Kuadratik denklemlerde öğrencinin yazdığı adımları
    SymPy kullanarak cebirsel olarak doğrular.
    eval() ve exec() kullanmaz; katı AST beyaz liste denetimi uygular.
    """

    MAX_AST_DEPTH = 15
    ALLOWED_VARIABLES = {
        "x", "y", "z", "a", "b", "c", "k", "n", "m", "r", "p", "q", "d", "Delta", "P", "Q", "R",
        "theta", "alpha", "beta", "pi", "e",
        "h", "dx", "dy", "dt", "u", "v", "w", "t", "oo", "inf", "C"
    }
    ALLOWED_FUNCTIONS = {
        "sqrt", "Abs", "degree", "rem", "quo", "Poly",
        "sin", "cos", "tan", "cot", "sec", "csc",
        "asin", "acos", "atan",
        "log", "ln", "exp",
        "diff", "limit", "Derivative", "Limit",
        "integrate", "Integral"
    }

    def __init__(self):
        # SymPy sembolleri
        self.symbols = {name: sp.Symbol(name) for name in self.ALLOWED_VARIABLES}
        self.symbols["pi"] = sp.pi
        self.symbols["e"] = sp.E
        self.symbols["oo"] = sp.oo
        self.symbols["inf"] = sp.oo
        self.symbols["sqrt"] = sp.sqrt
        self.symbols["Abs"] = sp.Abs
        self.symbols["degree"] = sp.degree
        self.symbols["rem"] = sp.rem
        self.symbols["quo"] = sp.quo
        self.symbols["Poly"] = sp.Poly
        self.symbols["sin"] = sp.sin
        self.symbols["cos"] = sp.cos
        self.symbols["tan"] = sp.tan
        self.symbols["cot"] = sp.cot
        self.symbols["sec"] = sp.sec
        self.symbols["csc"] = sp.csc
        self.symbols["asin"] = sp.asin
        self.symbols["acos"] = sp.acos
        self.symbols["atan"] = sp.atan
        self.symbols["log"] = sp.log
        self.symbols["ln"] = sp.log
        self.symbols["exp"] = sp.exp
        self.symbols["diff"] = sp.diff
        self.symbols["limit"] = sp.limit
        self.symbols["Derivative"] = sp.Derivative
        self.symbols["Limit"] = sp.Limit
        self.symbols["integrate"] = sp.integrate
        self.symbols["Integral"] = sp.Integral

        # Eşdeğerlik LRU önbelleği (Tekrar eden adımlarda <0.1ms hızlı yol)
        self._cache: dict = {}

        # SymPy soğuk başlangıç (cold-start) gecikmesini önlemek için motoru ısıt (warm-up)
        try:
            _ = self.parse_to_sympy("x + 1 = 2")
            _ = sp.simplify(self.symbols["x"] - self.symbols["x"])
        except Exception:
            pass


    def sanitize_and_validate_ast(self, raw_str: str) -> None:
        """
        Girdi metnini Python AST seviyesinde inceler.
        Yasaklı fonksiyon çağrılarını, modül yüklemelerini ve derinlik aşımlarını engeller.
        """
        # Örtük çarpma ve mobil doğal sözdizimi ön-işlemesi
        normalized = ImplicitMultiplicationPreprocessor.preprocess(raw_str)

        # Eşittir işaretini geçici olarak kaldırıp iki tarafı ayrı parse et
        parts = normalized.split("=")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            try:
                tree = ast.parse(part, mode="eval")
            except SyntaxError as e:
                raise ValueError(f"Sözdizimi hatası: {e}")

            # Derinlik ve düğüm denetimi
            self._check_ast_safety(tree, current_depth=0)

    def _check_ast_safety(self, node: ast.AST, current_depth: int) -> None:
        if current_depth > self.MAX_AST_DEPTH:
            raise SecurityViolationError(f"AST derinlik sınırı aşıldı (> {self.MAX_AST_DEPTH})")

        # İzin verilen düğüm türleri
        allowed_types = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Constant,
            ast.Name,
            ast.Call,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.Pow,
            ast.USub,
            ast.UAdd,
            ast.Load,
        )

        if not isinstance(node, allowed_types):
            raise SecurityViolationError(f"Yasaklı AST düğümü tespit edildi: {type(node).__name__}")

        if isinstance(node, ast.Name):
            if node.id not in self.ALLOWED_VARIABLES and node.id not in self.ALLOWED_FUNCTIONS:
                raise SecurityViolationError(f"Tanımsız veya yetkisiz değişken/fonksiyon: '{node.id}'")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in self.ALLOWED_FUNCTIONS:
                func_name = getattr(node.func, "id", "unknown")
                raise SecurityViolationError(f"Yasaklı fonksiyon çağrısı: '{func_name}'")

        for child in ast.iter_child_nodes(node):
            self._check_ast_safety(child, current_depth + 1)

    def parse_to_sympy(self, expr_str: str) -> sp.Expr:
        """
        Metin halindeki ifadeyi güvenli bir şekilde SymPy ifadesine dönüştürür.
        Denklem ise (LHS = RHS) -> LHS - (RHS) formuna indirger.
        """
        expr_str = ImplicitMultiplicationPreprocessor.preprocess(expr_str)
        self.sanitize_and_validate_ast(expr_str)

        if "=" in expr_str:
            parts = expr_str.split("=")
            if len(parts) != 2:
                raise ValueError("Denklemde birden fazla '=' işareti bulunamaz.")
            lhs_str = parts[0].strip()
            rhs_str = parts[1].strip()
            lhs = sp.sympify(lhs_str, locals=self.symbols)
            rhs = sp.sympify(rhs_str, locals=self.symbols)
            return sp.simplify(lhs - rhs)
        else:
            return sp.sympify(expr_str, locals=self.symbols)

    def verify_equivalence(
        self, user_expr_str: str, target_expr_str: str
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Kullanıcı ifadesinin hedef ifadeyle cebirsel olarak eşdeğer olup olmadığını doğrular.
        Returns: (is_equivalent, elapsed_ms, canonical_diff_repr)
        """
        start_time = time.perf_counter()
        cache_key = (user_expr_str.strip(), target_expr_str.strip())
        if cache_key in self._cache:
            is_eq, diff_repr = self._cache[cache_key]
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return is_eq, elapsed_ms, diff_repr

        try:
            user_expr = self.parse_to_sympy(user_expr_str)
            target_expr = self.parse_to_sympy(target_expr_str)

            # 1. Doğrudan fark testi: user_expr - target_expr == 0 ?
            diff = sp.simplify(user_expr - target_expr)
            if diff == 0:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                if len(self._cache) > 2048:
                    self._cache.clear()
                self._cache[cache_key] = (True, "0")
                return True, elapsed_ms, "0"

            # 2. Skaler kat denklem eşdeğerliği (c * target_expr == user_expr, c != 0)
            if target_expr != 0 and user_expr != 0:
                try:
                    ratio = sp.simplify(user_expr / target_expr)
                    if ratio.is_number and ratio != 0:
                        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                        if len(self._cache) > 2048:
                            self._cache.clear()
                        self._cache[cache_key] = (True, "0")
                        return True, elapsed_ms, "0"
                except Exception:
                    pass

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            diff_str = str(diff)
            if len(self._cache) > 2048:
                self._cache.clear()
            self._cache[cache_key] = (False, diff_str)
            return False, elapsed_ms, diff_str
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            raise e

    def polynomial_divide(self, p_str: str, b_str: str) -> Tuple[sp.Expr, sp.Expr]:
        """
        Polinom bölmesini hesaplar: P(x) / B(x) -> (Q(x), K(x))
        P(x) = B(x) * Q(x) + K(x)
        """
        p_expr = self.parse_to_sympy(p_str)
        b_expr = self.parse_to_sympy(b_str)
        x = self.symbols["x"]
        quo, rem = sp.div(p_expr, b_expr, x)
        return quo, rem

    def polynomial_remainder(self, p_str: str, b_str: str) -> sp.Expr:
        """P(x)'in B(x)'e bölümünden kalanı (rem) döndürür."""
        _, rem = self.polynomial_divide(p_str, b_str)
        return rem

    def polynomial_coeffs_sum(self, p_str: str) -> sp.Expr:
        """P(x) için katsayılar toplamını hesaplar: P(1)."""
        p_expr = self.parse_to_sympy(p_str)
        x = self.symbols["x"]
        return sp.simplify(p_expr.subs(x, 1))

    def polynomial_constant_term(self, p_str: str) -> sp.Expr:
        """P(x) için sabit terimi hesaplar: P(0)."""
        p_expr = self.parse_to_sympy(p_str)
        x = self.symbols["x"]
        return sp.simplify(p_expr.subs(x, 0))

    def verify_parabola_vertex(self, a_val: float, b_val: float, c_val: float) -> Tuple[float, float]:
        """Parabol tepe noktası T(r, k) koordinatlarını hesaplar: r = -b/(2a), k = c - b²/(4a)."""
        if a_val == 0:
            raise ValueError("İkinci dereceden fonksiyonda a katsayısı 0 olamaz.")
        r = -b_val / (2.0 * a_val)
        k = c_val - (b_val ** 2) / (4.0 * a_val)
        return r, k

    def evaluate_domain_constraints(
        self, expr_str: str, variable: str = "x", candidate_val: float = 0.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Verilen bir ifadenin aday kök (candidate_val) değerinde tanım kümesi kısıtlarını
        sağlayıp sağlamadığını doğrular.
        - Logaritma argümanları > 0 olmalı.
        - Logaritma tabanları > 0 ve != 1 olmalı.
        - Karekök içleri >= 0 olmalı.
        - Paydalar != 0 olmalı (ifade sonlu ve gerçel olmalı).
        """
        expr = self.parse_to_sympy(expr_str)
        var_sym = self.symbols.get(variable, sp.Symbol(variable))

        # 1. Logaritma denetimi
        for l in expr.atoms(sp.log):
            arg_val = sp.sympify(l.args[0]).subs(var_sym, candidate_val).evalf()
            if not arg_val.is_real or float(arg_val) <= 0:
                return False, f"Logaritma argümanı pozitif olmalıdır: {l.args[0]} = {arg_val} <= 0"
            if len(l.args) > 1:
                base_val = sp.sympify(l.args[1]).subs(var_sym, candidate_val).evalf()
                if not base_val.is_real or float(base_val) <= 0 or abs(float(base_val) - 1.0) < 1e-9:
                    return False, f"Logaritma tabanı pozitif ve 1'den farklı olmalıdır: {l.args[1]} = {base_val}"

        # 2. Karekök ve çift dereceli kök denetimi
        for p in expr.atoms(sp.Pow):
            base, exp = p.args
            if hasattr(exp, "is_Rational") and exp.is_Rational and exp.q % 2 == 0:
                arg_val = sp.sympify(base).subs(var_sym, candidate_val).evalf()
                if not arg_val.is_real or float(arg_val) < 0:
                    return False, f"Karekök içi negatif olamaz: {base} = {arg_val} < 0"

        # 3. Payda, tanımsızlık ve dikey asimptot denetimi
        evaluated = expr.subs(var_sym, candidate_val).evalf()
        if (
            evaluated in (sp.nan, sp.zoo)
            or not evaluated.is_finite
            or not evaluated.is_real
            or abs(float(evaluated)) > 1e10
        ):
            return False, f"İfade {variable} = {candidate_val} için tanımsız veya gerçel değil."

        return True, None

    def verify_trig_identity(self, lhs_str: str, rhs_str: str) -> bool:
        """İki trigonometrik ifadenin özdeşliğini doğrular."""
        lhs = self.parse_to_sympy(lhs_str)
        rhs = self.parse_to_sympy(rhs_str)
        diff = sp.simplify(lhs - rhs)
        if diff == 0:
            return True
        if sp.trigsimp(diff) == 0:
            return True
        # Tan/cot/sec/csc içeren ifadeleri sin/cos cinsinden yeniden yazarak sadeleştir
        rewritten = diff.rewrite(sp.sin)
        return sp.simplify(sp.trigsimp(rewritten)) == 0

    def verify_log_equality(self, lhs_str: str, rhs_str: str) -> bool:
        """İki logaritmik ifadenin denkliğini doğrular."""
        lhs = self.parse_to_sympy(lhs_str)
        rhs = self.parse_to_sympy(rhs_str)
        diff = sp.simplify(lhs - rhs)
        if diff == 0:
            return True
        expanded_diff = sp.expand_log(diff, force=True)
        return sp.simplify(expanded_diff) == 0

    def compute_limit(
        self, expr_str: str, var: str = "x", target_val: Any = 0, dir_str: str = "+-"
    ) -> Tuple[sp.Expr, bool]:
        """
        Verilen ifadenin limitini hesaplar.
        Returns: (limit_değeri, sonlu_mu)
        """
        expr = self.parse_to_sympy(expr_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))

        if target_val in ("oo", "inf", sp.oo):
            target = sp.oo
        elif target_val in ("-oo", "-inf", -sp.oo):
            target = -sp.oo
        else:
            target = sp.sympify(target_val, locals=self.symbols)

        lim = sp.limit(expr, var_sym, target, dir=dir_str)
        is_finite = bool(lim.is_finite if hasattr(lim, "is_finite") else True)
        return lim, is_finite

    def compute_derivative(self, expr_str: str, var: str = "x", order: int = 1) -> sp.Expr:
        """İfadenin belirtilen değişkene göre n. dereceden türevini hesaplar."""
        expr = self.parse_to_sympy(expr_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))
        return sp.diff(expr, var_sym, order)

    def verify_derivative(self, expr_str: str, candidate_deriv_str: str, var: str = "x") -> bool:
        """Öğrencinin türev adımının doğruluğunu teyit eder."""
        actual = self.compute_derivative(expr_str, var=var)
        candidate = self.parse_to_sympy(candidate_deriv_str)
        diff = sp.simplify(actual - candidate)
        if diff == 0:
            return True
        if sp.trigsimp(diff) == 0:
            return True
        return False

    def compute_tangent_line(self, func_str: str, x0: float) -> Tuple[sp.Expr, float, float]:
        """
        f(x) eğrisine x0 noktasındaki teğet doğrusunun denklemini ve eğimini hesaplar.
        Returns: (teğet_denklemi, eğim, y0)
        """
        expr = self.parse_to_sympy(func_str)
        x = self.symbols.get("x", sp.Symbol("x"))
        y0_val = expr.subs(x, x0).evalf()
        deriv = sp.diff(expr, x)
        slope_val = deriv.subs(x, x0).evalf()

        y0 = float(y0_val)
        slope = float(slope_val)
        tangent_expr = sp.simplify(slope * (x - x0) + y0)
        return tangent_expr, slope, y0

    def check_continuity(
        self, expr_str: str, var: str = "x", pt: float = 0.0
    ) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Fonksiyonun verilen noktada sürekli olup olmadığını denetler.
        Returns: (is_continuous, limit_val, function_val)
        """
        expr = self.parse_to_sympy(expr_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))

        try:
            left_lim = sp.limit(expr, var_sym, pt, dir="-")
            right_lim = sp.limit(expr, var_sym, pt, dir="+")
            func_val = expr.subs(var_sym, pt).evalf()

            if not (left_lim.is_finite and right_lim.is_finite and func_val.is_finite):
                return False, None, None

            left_f = float(left_lim.evalf())
            right_f = float(right_lim.evalf())
            val_f = float(func_val)

            if abs(left_f - right_f) < 1e-7 and abs(left_f - val_f) < 1e-7:
                return True, left_f, val_f
            else:
                lim_f = left_f if abs(left_f - right_f) < 1e-7 else None
                return False, lim_f, val_f
        except Exception:
            return False, None, None

    def compute_indefinite_integral(
        self, expr_str: str, var: str = "x", add_constant: bool = True
    ) -> sp.Expr:
        """
        Belirsiz integrali hesaplar: int f(x)dx = F(x) + C.
        """
        expr = self.parse_to_sympy(expr_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))
        antideriv = sp.integrate(expr, var_sym)
        if add_constant:
            antideriv = antideriv + self.symbols["C"]
        return antideriv

    def compute_definite_integral(
        self, expr_str: str, var: str = "x", a: Any = 0, b: Any = 1
    ) -> Tuple[sp.Expr, float]:
        """
        Belirli integrali hesaplar: int_a^b f(x)dx.
        Returns: (tam_sembolik_deger, ondalikli_sayi)
        """
        expr = self.parse_to_sympy(expr_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))

        lower = sp.oo if a in ("oo", "inf") else (-sp.oo if a in ("-oo", "-inf") else sp.sympify(a, locals=self.symbols))
        upper = sp.oo if b in ("oo", "inf") else (-sp.oo if b in ("-oo", "-inf") else sp.sympify(b, locals=self.symbols))

        exact = sp.integrate(expr, (var_sym, lower, upper))
        val = float(exact.evalf())
        return exact, val

    def compute_area_between_curves(
        self, f_str: str, g_str: str, a: float, b: float
    ) -> float:
        """
        İki eğri arasında kalan geometrik alanı hesaplar: int_a^b |f(x) - g(x)| dx.
        """
        f = self.parse_to_sympy(f_str)
        g = self.parse_to_sympy(g_str)
        x = self.symbols.get("x", sp.Symbol("x"))
        area = sp.integrate(sp.Abs(f - g), (x, a, b))
        return float(area.evalf())

    def verify_integral(
        self, integrand_str: str, candidate_integral_str: str, var: str = "x"
    ) -> bool:
        """
        Öğrencinin bulduğu belirsiz integralin doğruluğunu (türevini alarak) teyit eder.
        d/dx [Candidate(x)] == Integrand(x) ?
        """
        integrand = self.parse_to_sympy(integrand_str)
        candidate = self.parse_to_sympy(candidate_integral_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))

        deriv = sp.diff(candidate, var_sym)
        diff = sp.simplify(deriv - integrand)
        if diff == 0:
            return True
        if sp.trigsimp(diff) == 0:
            return True
        return False

    def compute_riemann_sum(
        self, expr_str: str, a: float, b: float, n: int, method: str = "midpoint"
    ) -> float:
        """
        Riemann toplamını hesaplar (sol, sağ, orta nokta).
        """
        if n <= 0:
            raise ValueError("Alt aralık sayısı n pozitif tam sayı olmalıdır.")

        expr = self.parse_to_sympy(expr_str)
        x = self.symbols.get("x", sp.Symbol("x"))
        dx = (b - a) / float(n)
        total = 0.0

        for i in range(n):
            if method == "left":
                xi = a + i * dx
            elif method == "right":
                xi = a + (i + 1) * dx
            else:  # midpoint
                xi = a + (i + 0.5) * dx

            yi = float(expr.subs(x, xi).evalf())
            total += yi * dx

        return round(total, 6)


