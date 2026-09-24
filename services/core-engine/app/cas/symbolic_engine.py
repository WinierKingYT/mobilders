import ast
from collections import OrderedDict
import concurrent.futures
import time
from typing import Tuple, Optional, Set, Any
import sympy as sp
from app.cas.preprocessor import ImplicitMultiplicationPreprocessor
from app.core.config import settings


class SecurityViolationError(Exception):
    """AST güvenlik ihlali durumunda fırlatılır."""
    pass


class CASTimeoutError(Exception):
    """CAS sembolik hesaplama zaman aşımına uğradığında fırlatılır."""
    pass


class SymbolicEquivalenceEngine:
    """
    Kuadratik denklemlerde öğrencinin yazdığı adımları
    SymPy kullanarak cebirsel olarak doğrular.
    eval() ve exec() kullanmaz; katı AST beyaz liste denetimi ve zaman aşımı koruması uygular.
    """

    MAX_CACHE_SIZE = 2048
    MAX_POLYNOMIAL_DEGREE = 12
    ALLOWED_VARIABLES = {
        "x", "y", "z", "a", "b", "c", "k", "n", "m", "r", "p", "q", "d", "Delta", "P", "Q", "R",
        "theta", "alpha", "beta", "pi", "e",
        "h", "dx", "dy", "dt", "u", "v", "w", "t", "oo", "inf", "C",
        "X", "Y", "Z", "A", "B", "T"
    }
    ALLOWED_FUNCTIONS = {
        "sqrt", "Abs", "degree", "rem", "quo", "Poly",
        "sin", "cos", "tan", "cot", "sec", "csc",
        "asin", "acos", "atan",
        "log", "ln", "log10", "exp",
        "diff", "limit", "Derivative", "Limit",
        "integrate", "Integral"
    }

    def __init__(
        self,
        timeout_ms: Optional[int] = None,
        max_ast_depth: Optional[int] = None,
    ):
        self.timeout_ms = timeout_ms if timeout_ms is not None else settings.CAS_TIMEOUT_MS
        self.max_ast_depth = max_ast_depth if max_ast_depth is not None else settings.MAX_AST_DEPTH
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        # SymPy sembolleri
        self.symbols = {name: sp.Symbol(name) for name in self.ALLOWED_VARIABLES}
        # Büyük harf değişkenleri küçük harf sembollerine bağla (X -> x)
        for cap in ["X", "Y", "Z", "A", "B", "T"]:
            if cap.lower() in self.symbols:
                self.symbols[cap] = self.symbols[cap.lower()]
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
        self.symbols["log10"] = lambda arg: sp.log(arg, 10)
        self.symbols["exp"] = sp.exp
        self.symbols["diff"] = sp.diff
        self.symbols["limit"] = sp.limit
        self.symbols["Derivative"] = sp.Derivative
        self.symbols["Limit"] = sp.Limit
        self.symbols["integrate"] = sp.integrate
        self.symbols["Integral"] = sp.Integral

        # Eşdeğerlik LRU önbelleği (Tekrar eden adımlarda <0.1ms hızlı yol)
        self._cache: OrderedDict[Tuple[str, str], Tuple[bool, Optional[str]]] = OrderedDict()

        # SymPy soğuk başlangıç (cold-start) gecikmesini önlemek için motoru ısıt (warm-up)
        try:
            _ = self.parse_to_sympy("x + 1 = 2")
            _ = sp.simplify(self.symbols["x"] - self.symbols["x"])
        except Exception:
            pass

    def shutdown(self, wait: bool = False) -> None:
        """Kapatma sırasında iş parçacığı havuzunu temizler."""
        if hasattr(self, "_executor") and self._executor:
            try:
                self._executor.shutdown(wait=wait, cancel_futures=True)
            except Exception:
                pass

    def __del__(self) -> None:
        try:
            self.shutdown(wait=False)
        except Exception:
            pass

    def __enter__(self) -> "SymbolicEquivalenceEngine":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.shutdown(wait=False)

    def _cache_get(self, key: Tuple[str, str]) -> Optional[Tuple[bool, Optional[str]]]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def _cache_put(self, key: Tuple[str, str], val: Tuple[bool, Optional[str]]) -> None:
        self._cache[key] = val
        self._cache.move_to_end(key)
        if len(self._cache) > self.MAX_CACHE_SIZE:
            self._cache.popitem(last=False)


    def sanitize_and_validate_ast(self, raw_str: str) -> None:
        """
        Aşama 54: Girdi metnini Python AST seviyesinde inceler.
        Yasaklı fonksiyon çağrılarını, modül yüklemelerini, dunder ('__'), import, exec
        ifadelerini ve kod enjeksiyon vektörlerini tamamen engeller (Zero-Execution).
        """
        # Aşama 54: Token Beyaz Liste & Kod Enjeksiyon Ön Kontrolleri
        raw_lower = raw_str.lower()
        forbidden_tokens = ["__", "import", "exec", "eval", "compile", "globals", "locals", "builtins", "open", "system", "subprocess", "lambda"]
        for token in forbidden_tokens:
            if token in raw_lower:
                raise SecurityViolationError(f"Güvenlik İhlali: Yasaklı kod enjeksiyon ifadesi tespit edildi: '{token}'")

        # Örtük çarpma ve mobil doğal sözdizimi ön-işlemesi
        normalized = ImplicitMultiplicationPreprocessor.preprocess(raw_str)

        # DoS guard: reject expressions with extreme parenthesis depth before calling ast.parse
        if normalized.count("(") > self.max_ast_depth or normalized.count(")") > self.max_ast_depth:
            raise SecurityViolationError(
                f"Aşırı parantez derinliği tespit edildi (> {self.max_ast_depth})"
            )

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
            except RecursionError:
                raise SecurityViolationError("Aşırı parantez derinliği veya döngüsel sözdizimi (RecursionError)")

            # Derinlik ve düğüm denetimi
            self._check_ast_safety(tree, current_depth=0)

    def _check_ast_safety(self, node: ast.AST, current_depth: int) -> None:
        if current_depth > self.max_ast_depth:
            raise SecurityViolationError(f"AST derinlik sınırı aşıldı (> {self.max_ast_depth})")

        # Aşama 54: İzin verilen matematiksel AST düğüm türleri beyaz listesi
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

        # Sabit denetimi: Yalnızca int, float, complex sayılara izin verilir (string/bytes yasaktır)
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float, complex)):
                raise SecurityViolationError(f"Güvenlik İhlali: Yasaklı sabit türü '{type(node.value).__name__}'. Sadece sayısal değerler kabul edilir.")

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            exp_val = None
            if isinstance(node.right, ast.Constant) and isinstance(node.right.value, (int, float)):
                exp_val = abs(node.right.value)
            elif isinstance(node.right, ast.UnaryOp) and isinstance(node.right.op, (ast.USub, ast.UAdd)):
                if isinstance(node.right.operand, ast.Constant) and isinstance(node.right.operand.value, (int, float)):
                    exp_val = abs(node.right.operand.value)
            if exp_val is not None and exp_val > self.MAX_POLYNOMIAL_DEGREE:
                raise SecurityViolationError(f"Aşırı derece/üs tespit edildi: {exp_val} (> {self.MAX_POLYNOMIAL_DEGREE})")

        if isinstance(node, ast.Name):
            if "__" in node.id or node.id.lower() in {"import", "exec", "eval", "compile", "globals", "locals", "open"}:
                raise SecurityViolationError(f"Güvenlik İhlali: Yasaklı değişken veya anahtar kelime: '{node.id}'")
            if node.id not in self.ALLOWED_VARIABLES and node.id not in self.ALLOWED_FUNCTIONS:
                raise SecurityViolationError(f"Tanımsız veya yetkisiz değişken/fonksiyon: '{node.id}'")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in self.ALLOWED_FUNCTIONS:
                func_name = getattr(node.func, "id", "unknown")
                raise SecurityViolationError(f"Yasaklı fonksiyon çağrısı: '{func_name}'")
            if node.keywords:
                raise SecurityViolationError("Güvenlik İhlali: Fonksiyonlarda isimli parametreler (keywords) yasaktır.")

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
                raise ValueError("Denklemde tam olarak bir '=' işareti bulunmalıdır.")
            lhs_str = parts[0].strip()
            rhs_str = parts[1].strip()
            if not lhs_str or not rhs_str:
                raise ValueError("Eşitliğin her iki tarafında da geçerli bir matematiksel ifade bulunmalıdır.")
            try:
                lhs = sp.sympify(lhs_str, locals=self.symbols)
                rhs = sp.sympify(rhs_str, locals=self.symbols)
            except ZeroDivisionError:
                raise ValueError("Tanımsız rasyonel ifade (sıfıra bölme hatası)")

            if lhs in (sp.zoo, sp.nan) or rhs in (sp.zoo, sp.nan) or lhs.has(sp.zoo, sp.nan) or rhs.has(sp.zoo, sp.nan):
                raise ValueError("Tanımsız rasyonel ifade (zoo / nan tespit edildi)")

            res = sp.simplify(lhs - rhs)
            if res in (sp.zoo, sp.nan) or res.has(sp.zoo, sp.nan):
                raise ValueError("Tanımsız rasyonel ifade (zoo / nan tespit edildi)")

            try:
                for var in (res.free_symbols or []):
                    if res.is_polynomial(var):
                        deg = sp.degree(res, var)
                        if deg is not None and deg > self.MAX_POLYNOMIAL_DEGREE:
                            raise SecurityViolationError(f"Aşırı polinom derecesi tespit edildi: {deg} (> {self.MAX_POLYNOMIAL_DEGREE})")
            except Exception as e:
                if isinstance(e, SecurityViolationError):
                    raise
            return res
        else:
            try:
                res = sp.sympify(expr_str, locals=self.symbols)
            except ZeroDivisionError:
                raise ValueError("Tanımsız rasyonel ifade (sıfıra bölme hatası)")

            if res in (sp.zoo, sp.nan) or res.has(sp.zoo, sp.nan):
                raise ValueError("Tanımsız rasyonel ifade (zoo / nan tespit edildi)")

            try:
                for var in (res.free_symbols or []):
                    if res.is_polynomial(var):
                        deg = sp.degree(res, var)
                        if deg is not None and deg > self.MAX_POLYNOMIAL_DEGREE:
                            raise SecurityViolationError(f"Aşırı polinom derecesi tespit edildi: {deg} (> {self.MAX_POLYNOMIAL_DEGREE})")
            except Exception as e:
                if isinstance(e, SecurityViolationError):
                    raise
            return res

    def _compute_equivalence(
        self, user_expr_str: str, target_expr_str: str
    ) -> Tuple[bool, Optional[str]]:
        try:
            user_expr = self.parse_to_sympy(user_expr_str)
            target_expr = self.parse_to_sympy(target_expr_str)
        except ValueError as ve:
            if "tanımsız" in str(ve).lower() or "sıfıra bölme" in str(ve).lower():
                return False, "Tanımsız rasyonel ifade"
            raise

        if user_expr in (sp.zoo, sp.nan) or target_expr in (sp.zoo, sp.nan):
            return False, "Tanımsız rasyonel ifade"
        if user_expr.has(sp.zoo, sp.nan) or target_expr.has(sp.zoo, sp.nan):
            return False, "Tanımsız rasyonel ifade"

        # 1. Doğrudan fark testi: user_expr - target_expr == 0 ?
        try:
            diff = sp.simplify(user_expr - target_expr)
        except (ZeroDivisionError, Exception):
            return False, "Tanımsız rasyonel ifade"

        if diff in (sp.zoo, sp.nan) or diff.has(sp.zoo, sp.nan):
            return False, "Tanımsız rasyonel ifade"

        if diff == 0 or getattr(diff, "is_zero", False):
            return True, "0"

        # Trigonometrik sadeleştirme fallback'i (sp.trigsimp ve sin rewrite)
        try:
            trig_diff = sp.trigsimp(diff)
            if trig_diff == 0 or getattr(trig_diff, "is_zero", False):
                return True, "0"
            if any(func in str(diff) for func in ("tan", "cot", "sec", "csc")):
                rewritten_diff = sp.trigsimp(diff.rewrite(sp.sin))
                if rewritten_diff == 0 or getattr(rewritten_diff, "is_zero", False):
                    return True, "0"
        except Exception:
            pass

        # Logaritmik sadeleştirme fallback'i (sp.expand_log)
        try:
            log_diff = sp.simplify(sp.expand_log(diff, force=True))
            if log_diff == 0 or getattr(log_diff, "is_zero", False):
                return True, "0"
        except Exception:
            pass

        # 2. Skaler kat denklem eşdeğerliği (c * target_expr == user_expr, c != 0)
        # Yalnızca denklemlerde (LHS = RHS) geçerlidir; türev veya fonksiyon değerlerinde skaler kat eşit kabul edilemez.
        if ("=" in user_expr_str or "=" in target_expr_str) and target_expr != 0 and user_expr != 0:
            try:
                ratio = sp.simplify(user_expr / target_expr)
                if ratio in (sp.zoo, sp.nan) or ratio.has(sp.zoo, sp.nan):
                    return False, "Tanımsız rasyonel ifade"
                if ratio.is_number and ratio != 0:
                    return True, "0"
            except Exception:
                pass

        return False, str(diff)

    def verify_equivalence(
        self, user_expr_str: str, target_expr_str: str, timeout_ms: Optional[int] = None
    ) -> Tuple[bool, float, Optional[str]]:
        """
        Kullanıcı ifadesinin hedef ifadeyle cebirsel olarak eşdeğer olup olmadığını doğrular.
        Returns: (is_equivalent, elapsed_ms, canonical_diff_repr)
        """
        start_time = time.perf_counter()
        cache_key = (user_expr_str.strip(), target_expr_str.strip())
        cached = self._cache_get(cache_key)
        if cached is not None:
            is_eq, diff_repr = cached
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return is_eq, elapsed_ms, diff_repr

        effective_timeout_ms = timeout_ms if timeout_ms is not None else self.timeout_ms
        timeout_sec = (effective_timeout_ms / 1000.0) if effective_timeout_ms and effective_timeout_ms > 0 else None

        try:
            if timeout_sec is not None:
                future = self._executor.submit(self._compute_equivalence, user_expr_str, target_expr_str)
                try:
                    is_equiv, diff_str = future.result(timeout=timeout_sec)
                except concurrent.futures.TimeoutError:
                    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                    raise CASTimeoutError(
                        f"CAS sembolik doğrulama {effective_timeout_ms}ms zaman aşımına uğradı."
                    )
            else:
                is_equiv, diff_str = self._compute_equivalence(user_expr_str, target_expr_str)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self._cache_put(cache_key, (is_equiv, diff_str))
            return is_equiv, elapsed_ms, diff_str
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

    def detect_root_loss(
        self, original_eq_str: str, simplified_eq_str: str, var: str = "x"
    ) -> Tuple[bool, Set[Any]]:
        """
        Denklem sadeleştirmelerinde (örneğin x*(x - 2) = 0 -> x - 2 = 0)
        sıfır veya diğer köklerin kaybolup kaybolmadığını denetler.
        Returns: (has_root_loss, missing_roots)
        """
        orig_expr = self.parse_to_sympy(original_eq_str)
        simp_expr = self.parse_to_sympy(simplified_eq_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))

        try:
            orig_roots = set(sp.solve(orig_expr, var_sym))
            simp_roots = set(sp.solve(simp_expr, var_sym))
            missing = orig_roots - simp_roots
            return (len(missing) > 0, missing)
        except Exception:
            return (False, set())

    def verify_inequality_step(
        self, prev_ineq_str: str, next_ineq_str: str, var: str = "x"
    ) -> Tuple[bool, Optional[str]]:
        """
        Eşitsizlik adımlarının (örneğin -2*x < 6 -> x > -3) doğruluğunu ve
        negatif çarpan/bölenlerde yön değiştirme kuralına uyulup uyulmadığını doğrular.
        Returns: (is_valid, feedback_message)
        """
        prev_clean = ImplicitMultiplicationPreprocessor.preprocess(prev_ineq_str)
        next_clean = ImplicitMultiplicationPreprocessor.preprocess(next_ineq_str)
        var_sym = self.symbols.get(var, sp.Symbol(var))

        try:
            prev_sym = sp.sympify(prev_clean, locals=self.symbols)
            next_sym = sp.sympify(next_clean, locals=self.symbols)
            prev_sol = sp.reduce_inequalities(prev_sym, var_sym)
            next_sol = sp.reduce_inequalities(next_sym, var_sym)

            if prev_sol == next_sol:
                return True, None
            else:
                return False, "Eşitsizlik negatif bir sayı ile çarpıldığında veya bölündüğünde yön değiştirmelidir."
        except Exception as e:
            return False, f"Eşitsizlik çözümlenemedi: {e}"



