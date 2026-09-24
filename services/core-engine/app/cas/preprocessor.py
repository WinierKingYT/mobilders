import re

SUPERSCRIPT_MAP = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
}


class ImplicitMultiplicationPreprocessor:
    """
    Mobil cihazlarda öğrencinin sürekli '*' tuşuna basmasını önlemek amacıyla,
    doğal cebirsel yazımları ('2x', '(x+1)(x+3)', '4ac', 'x^2', 'x2', 'x²', '\\frac{1}{2}')
    SymPy ve Python AST ile uyumlu kanonik ifadelere dönüştürür.
    """

    @classmethod
    def preprocess(cls, text: str) -> str:
        if not text:
            return ""

        # DoS guard: limit text length to 1000 chars
        s = text.strip()[:1000]

        # 1. Unicode operatör ve karakter normalizasyonu
        s = s.replace("−", "-").replace("–", "-").replace("—", "-")
        s = s.replace("×", "*").replace("·", "*").replace("•", "*")
        s = s.replace("÷", "/")
        s = s.replace("±", "+")
        s = s.replace("^", "**")

        # Çift veya çoklu eşitlik normalizasyonu: == -> =
        s = re.sub(r"={2,}", "=", s)

        # İki nokta üst üste bölme normalizasyonu: 6 : 2 -> 6 / 2
        s = re.sub(r"(?<!:):(?!=)", "/", s)

        # 2. LaTeX operatör ve ayraç temizliği
        s = s.replace(r"\cdot", "*").replace(r"\times", "*")
        s = s.replace(r"\left(", "(").replace(r"\right)", ")")
        s = s.replace(r"\left[", "(").replace(r"\right]", ")")
        s = s.replace(r"\{", "(").replace(r"\}", ")")
        s = s.replace("[", "(").replace("]", ")")

        # 3. Bağımsız büyük harf değişkenleri küçük harfe normalize et (X -> x, Y -> y, Z -> z)
        # Kelime sınırı (\b) sayesinde Abs, Poly vb. fonksiyon isimleri bozulmaz
        s = re.sub(r"\b([XYZ])\b", lambda m: m.group(1).lower(), s)

        # 3. LaTeX kesirleri: \frac{a}{b} -> ((a)/(b))
        MAX_FRACTION_DEPTH = 12
        frac_iter = 0
        while r"\frac" in s and frac_iter < MAX_FRACTION_DEPTH:
            frac_iter += 1
            new_s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
            if new_s == s:
                new_s = re.sub(r"\\frac\s*([a-zA-Z0-9])\s*([a-zA-Z0-9])", r"((\1)/(\2))", s)
                if new_s == s:
                    break
            s = new_s

        if r"\frac" in s:
            # Fraction recursion depth exceeded: strip to prevent stack overflow/hang
            s = re.sub(r"\\frac", "", s)

        # 4. LaTeX karekök: \sqrt{a} -> sqrt(a)
        sqrt_iter = 0
        while r"\sqrt{" in s and sqrt_iter < 20:
            sqrt_iter += 1
            new_s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)
            if new_s == s:
                break
            s = new_s
        s = s.replace(r"\sqrt", "sqrt")

        # 5. Unicode üst simgeler: x² -> x**2, (x+1)³ -> (x+1)**3
        def _replace_superscripts(match):
            digits = "".join(SUPERSCRIPT_MAP[c] for c in match.group(1))
            return f"**{digits}"

        s = re.sub(r"([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", _replace_superscripts, s)

        # 6. Türkçe ondalık virgül desteği: 2,5 -> 2.5
        s = re.sub(r"(\d+),(\d+)", r"\1.\2", s)

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

        # 1. Kesir sonrası değişkenlerin deterministik parantezlenmesi: 1/2x -> ((1)/(2))*x
        s = re.sub(r"(\d+)\s*/\s*(\d+)\s*([a-zA-Z])", r"((\1)/(\2))*\3", s)

        # 2. 'x2' veya 'b2' gibi doğrudan yapışık üs yazımları: x2 -> x**2
        s = re.sub(r"\b([a-zA-Z])2\b", r"\1**2", s)

        # 3. Katsayı ile değişken arasına çarpma ekle: 2x -> 2*x, 12x -> 12*x, 3.5x -> 3.5*x
        s = re.sub(r"(\d+)([a-zA-Z])", r"\1*\2", s)

        # 4. Parantez çarpımları:
        # (x+1)(x+2) -> (x+1)*(x+2)
        s = re.sub(r"\)(\s*)\(", r")*\1(", s)

        # 5. Sayı veya değişken ile açılan parantez: 3(x+1) -> 3*(x+1), x(x+6) -> x*(x+6)
        # Ancak bilinen fonksiyon çağrılarını (sin, cos, tan, log, ln, sqrt, Poly vb.) koru
        known_functions = {
            "sqrt", "abs", "degree", "rem", "quo", "poly",
            "sin", "cos", "tan", "cot", "sec", "csc",
            "asin", "acos", "atan",
            "log", "ln", "exp",
            "diff", "limit", "derivative",
            "integrate", "integral"
        }

        def _paren_mult(match):
            prefix = match.group(1)
            ws = match.group(2)
            if prefix.lower() in known_functions:
                return f"{prefix}{ws}("
            return f"{prefix}*{ws}("

        s = re.sub(r"([a-zA-Z0-9_]+)(\s*)\(", _paren_mult, s)

        # 6. Kapanan parantez ile sayı veya değişken: (x+1)3 -> (x+1)*3, (x+1)x -> (x+1)*x
        s = re.sub(r"\)(\s*)(\d|[a-zA-Z])", r")*\1\2", s)

        # 7. Çoklu değişkenlerin örtük çarpımı: ab -> a*b, bc -> b*c, 2ab -> 2*a*b
        single_letter_vars = set("xyzabcknmrpqdutvwXYZABCT")
        def _expand_var_product(match):
            token = match.group(0)
            if token.lower() in known_functions or token in {"Delta", "pi", "oo", "inf"}:
                return token
            if len(token) >= 2 and all(c in single_letter_vars for c in token):
                return "*".join(list(token))
            return token

        s = re.sub(r"\b[a-zA-Z]{2,4}\b", _expand_var_product, s)

        # 8. Bilinen kuadratik terim kalıpları: '4ac' -> '4*a*c'
        s = re.sub(r"\b4ac\b", "4*a*c", s)
        s = re.sub(r"\b4\*a\*c\b", "4*a*c", s)

        # Çift '*' temizliği: Eğer yanlışlıkla '***' veya gereksiz boşluk oluştuysa
        s = re.sub(r"\*{3,}", "**", s)

        return s
