import ast
import time
from typing import Tuple, Optional, Set
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
    ALLOWED_VARIABLES = {"x", "y", "z", "a", "b", "c", "k", "n", "m", "Delta"}
    ALLOWED_FUNCTIONS = {"sqrt", "Abs"}

    def __init__(self):
        # SymPy sembolleri
        self.symbols = {name: sp.Symbol(name) for name in self.ALLOWED_VARIABLES}
        self.symbols["sqrt"] = sp.sqrt
        self.symbols["Abs"] = sp.Abs

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
        try:
            user_expr = self.parse_to_sympy(user_expr_str)
            target_expr = self.parse_to_sympy(target_expr_str)

            # 1. Doğrudan fark testi: user_expr - target_expr == 0 ?
            diff = sp.simplify(user_expr - target_expr)
            if diff == 0:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return True, elapsed_ms, "0"

            # 2. Skaler kat denklem eşdeğerliği (c * target_expr == user_expr, c != 0)
            if target_expr != 0 and user_expr != 0:
                try:
                    ratio = sp.simplify(user_expr / target_expr)
                    if ratio.is_number and ratio != 0:
                        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                        return True, elapsed_ms, "0"
                except Exception:
                    pass

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return False, elapsed_ms, str(diff)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            raise e
