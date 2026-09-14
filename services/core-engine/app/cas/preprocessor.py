import re


class ImplicitMultiplicationPreprocessor:
    """
    Mobil cihazlarda öğrencinin sürekli '*' tuşuna basmasını önlemek amacıyla,
    doğal cebirsel yazımları ('2x', '(x+1)(x+3)', '4ac', 'x^2', 'x2')
    SymPy ve Python AST ile uyumlu kanonik ifadelere dönüştürür.
    """

    @classmethod
    def preprocess(cls, text: str) -> str:
        if not text:
            return ""

        s = text.strip()

        # 1. LaTeX ve özel sembol temizliği
        s = s.replace("^", "**")
        s = s.replace("±", "+")

        # Eşittir içeren denklemlerde LHS ve RHS'yi ayrı işle
        if "=" in s:
            parts = s.split("=")
            processed_parts = [cls._preprocess_expression(p) for p in parts]
            return " = ".join(processed_parts)
        else:
            return cls._preprocess_expression(s)

    @classmethod
    def _preprocess_expression(cls, s: str) -> str:
        s = s.strip()
        if not s:
            return ""

        # 2. 'x2' veya 'b2' gibi doğrudan yapışık üs yazımları: x2 -> x**2 (önünde işlem veya parantez olan değişkenler)
        # Sadece değişkenin hemen ardından gelen 2 için (örn: x2 -> x**2, y2 -> y**2)
        s = re.sub(r"\b([a-zA-Z])2\b", r"\1**2", s)

        # 3. Katsayı ile değişken arasına çarpma ekle: 2x -> 2*x, 12x -> 12*x, 3.5x -> 3.5*x
        # Önünde veya arkasında '*' veya '**' olmamasına dikkat et
        s = re.sub(r"(\d+)([a-zA-Z])", r"\1*\2", s)

        # 4. Parantez çarpımları:
        # (x+1)(x+2) -> (x+1)*(x+2)
        s = re.sub(r"\)(\s*)\(", r")*\1(", s)

        # 5. Sayı veya değişken ile açılan parantez: 3(x+1) -> 3*(x+1), x(x+6) -> x*(x+6)
        # Ancak bilinen fonksiyon çağrılarını (sin, cos, tan, log, ln, sqrt, Poly vb.) koru
        known_functions = {
            "sqrt", "Abs", "degree", "rem", "quo", "Poly",
            "sin", "cos", "tan", "cot", "sec", "csc",
            "asin", "acos", "atan",
            "log", "ln", "exp"
        }

        def _paren_mult(match):
            prefix = match.group(1)
            ws = match.group(2)
            if prefix in known_functions:
                return f"{prefix}{ws}("
            return f"{prefix}*{ws}("

        s = re.sub(r"([a-zA-Z0-9_]+)(\s*)\(", _paren_mult, s)

        # 6. Kapanan parantez ile sayı veya değişken: (x+1)3 -> (x+1)*3, (x+1)x -> (x+1)*x
        s = re.sub(r"\)(\s*)(\d|[a-zA-Z])", r")*\1\2", s)

        # 7. Bilinen kuadratik terim kalıpları: '4ac' -> '4*a*c'
        s = re.sub(r"\b4ac\b", "4*a*c", s)
        s = re.sub(r"\b4\*a\*c\b", "4*a*c", s)

        # Çift '*' temizliği: Eğer yanlışlıkla '***' veya gereksiz boşluk oluştuysa
        s = re.sub(r"\*{3,}", "**", s)

        return s
