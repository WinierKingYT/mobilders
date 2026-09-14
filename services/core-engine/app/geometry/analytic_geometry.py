"""
Analitik Geometri ve 2B Vektörler Motoru (HEDEF 10)
Kartezyen koordinat sistemi, doğru analitiği, çember analitiği ve 2B vektör cebiri.
"""
from __future__ import annotations
import math
from typing import Optional, Tuple, Dict, Any, List
import sympy as sp


class Point2D:
    """Kartezyen düzlemde 2 boyutlu nokta nesnesi."""

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def distance_to(self, other: Point2D) -> float:
        """İki nokta arasındaki Öklid uzaklığı: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)"""
        return math.hypot(self.x - other.x, self.y - other.y)

    def midpoint_with(self, other: Point2D) -> Point2D:
        """İki noktanın orta noktası: M((x1+x2)/2, (y1+y2)/2)"""
        return Point2D((self.x + other.x) / 2.0, (self.y + other.y) / 2.0)

    def internal_division(self, other: Point2D, ratio_k: float) -> Point2D:
        """
        [AB] doğru parçasını k = AP / PB oranında içten bölen P noktası.
        x_p = (x_a + k * x_b) / (1 + k)
        y_p = (y_a + k * y_b) / (1 + k)
        """
        if ratio_k <= -1.0 or abs(1.0 + ratio_k) < 1e-9:
            raise ValueError("Bölme oranı k != -1 olmalıdır.")
        px = (self.x + ratio_k * other.x) / (1.0 + ratio_k)
        py = (self.y + ratio_k * other.y) / (1.0 + ratio_k)
        return Point2D(px, py)

    def quadrant(self) -> int:
        """Noktanın bulunduğu bölge (1, 2, 3, 4) veya eksen üzerindeyse 0."""
        if self.x > 0 and self.y > 0:
            return 1
        elif self.x < 0 and self.y > 0:
            return 2
        elif self.x < 0 and self.y < 0:
            return 3
        elif self.x > 0 and self.y < 0:
            return 4
        return 0

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"Point2D({self.x:g}, {self.y:g})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point2D):
            return False
        return math.isclose(self.x, other.x, abs_tol=1e-7) and math.isclose(self.y, other.y, abs_tol=1e-7)


class Line2D:
    """
    Kartezyen düzlemde doğru nesnesi: Ax + By + C = 0 genel formunda temsil edilir.
    """

    def __init__(self, A: float, B: float, C: float):
        if math.isclose(A, 0.0, abs_tol=1e-9) and math.isclose(B, 0.0, abs_tol=1e-9):
            raise ValueError("A ve B aynı anda sıfır olamaz!")
        # Standardize: make A >= 0 or first non-zero coefficient positive
        norm = math.hypot(A, B)
        self.A = float(A) / norm
        self.B = float(B) / norm
        self.C = float(C) / norm

    @classmethod
    def from_two_points(cls, p1: Point2D, p2: Point2D) -> Line2D:
        """İki noktadan geçen doğru denklemi."""
        if p1 == p2:
            raise ValueError("İki nokta birbirinden farklı olmalıdır!")
        # (y2 - y1)x - (x2 - x1)y + (x2*y1 - x1*y2) = 0
        A = p2.y - p1.y
        B = -(p2.x - p1.x)
        C = p2.x * p1.y - p1.x * p2.y
        return cls(A, B, C)

    @classmethod
    def from_point_and_slope(cls, p: Point2D, slope: float) -> Line2D:
        """Bir noktası ve eğimi verilen doğru denklemi: y - y1 = m(x - x1) => mx - y + (y1 - m*x1) = 0"""
        A = slope
        B = -1.0
        C = p.y - slope * p.x
        return cls(A, B, C)

    @classmethod
    def from_intercepts(cls, x_int: float, y_int: float) -> Line2D:
        """Eksenleri kestiği noktalar verilen doğru denklemi: x/a + y/b = 1 => bx + ay - ab = 0"""
        if math.isclose(x_int, 0.0, abs_tol=1e-9) or math.isclose(y_int, 0.0, abs_tol=1e-9):
            raise ValueError("Eksen kesimleri sıfır olamaz (orijinden geçen doğruda bu form kullanılamaz).")
        return cls(y_int, x_int, -x_int * y_int)

    @property
    def is_vertical(self) -> bool:
        """Düşey doğru kontrolü (B = 0, eğim tanımsız)."""
        return math.isclose(self.B, 0.0, abs_tol=1e-7)

    @property
    def is_horizontal(self) -> bool:
        """Yatay doğru kontrolü (A = 0, eğim = 0)."""
        return math.isclose(self.A, 0.0, abs_tol=1e-7)

    @property
    def slope(self) -> Optional[float]:
        """Doğrunun eğimi: m = -A / B (düşey doğrularda None)."""
        if self.is_vertical:
            return None
        return -self.A / self.B

    @property
    def angle_deg(self) -> float:
        """
        Doğrunun pozitif x-ekseniyle yaptığı eğim açısı (0° <= theta < 180°).
        """
        if self.is_vertical:
            return 90.0
        m = self.slope
        assert m is not None
        deg = math.degrees(math.atan(m))
        if deg < 0:
            deg += 180.0
        return deg

    @property
    def x_intercept(self) -> Optional[float]:
        """x-eksenini kestiği nokta apsisi (-C / A)."""
        if self.is_horizontal:
            return None
        return -self.C / self.A

    @property
    def y_intercept(self) -> Optional[float]:
        """y-eksenini kestiği nokta ordinatı (-C / B)."""
        if self.is_vertical:
            return None
        return -self.C / self.B

    def distance_from_point(self, point: Point2D) -> float:
        """Noktanın doğruya dik uzaklığı: d = |Ax0 + By0 + C| / sqrt(A^2 + B^2)"""
        # Normalleştirilmiş katsayılarda sqrt(A^2 + B^2) == 1
        return abs(self.A * point.x + self.B * point.y + self.C)

    def is_parallel_to(self, other: Line2D) -> bool:
        """Paralellik şartı: A1*B2 - A2*B1 == 0"""
        det = self.A * other.B - self.B * other.A
        return math.isclose(det, 0.0, abs_tol=1e-7)

    def is_perpendicular_to(self, other: Line2D) -> bool:
        """Diklik şartı: A1*A2 + B1*B2 == 0 (veya m1 * m2 == -1)"""
        dot = self.A * other.A + self.B * other.B
        return math.isclose(dot, 0.0, abs_tol=1e-7)

    def distance_to_parallel_line(self, other: Line2D) -> Optional[float]:
        """İki paralel doğru arasındaki uzaklık: |C1 - C2*sgn|"""
        if not self.is_parallel_to(other):
            return None
        # Katsayıların yönünü eşle
        sgn = 1.0 if (self.A * other.A + self.B * other.B) > 0 else -1.0
        return abs(self.C - sgn * other.C)

    def intersection_with(self, other: Line2D) -> Optional[Point2D]:
        """İki doğrunun kesişim noktası (paralel veya çakışık ise None)."""
        det = self.A * other.B - self.B * other.A
        if math.isclose(det, 0.0, abs_tol=1e-7):
            return None
        x = (self.B * other.C - other.B * self.C) / det
        y = (other.A * self.C - self.A * other.C) / det
        return Point2D(x, y)

    def __repr__(self) -> str:
        return f"Line2D({self.A:.3f}x + {self.B:.3f}y + {self.C:.3f} = 0)"


class Circle2D:
    """
    Kartezyen düzlemde çember nesnesi: (x - a)^2 + (y - b)^2 = r^2
    veya genel form: x^2 + y^2 + Dx + Ey + F = 0
    """

    def __init__(self, center: Point2D, radius: float):
        if radius <= 0:
            raise ValueError("Çember yarıçapı pozitif olmalıdır!")
        self.center = center
        self.radius = float(radius)

    @classmethod
    def from_general_form(cls, D: float, E: float, F: float) -> Circle2D:
        """
        x² + y² + Dx + Ey + F = 0 genel denkleminden standart çembere dönüşüm.
        Merkez M(-D/2, -E/2), Yarıçap r = 0.5 * sqrt(D² + E² - 4F)
        """
        discriminant = D * D + E * E - 4.0 * F
        if discriminant <= 0:
            raise ValueError(f"D² + E² - 4F = {discriminant} <= 0 olduğundan bir reel çember belirtmez!")
        center = Point2D(-D / 2.0, -E / 2.0)
        radius = 0.5 * math.sqrt(discriminant)
        return cls(center, radius)

    @property
    def area(self) -> float:
        return math.pi * self.radius * self.radius

    @property
    def circumference(self) -> float:
        return 2.0 * math.pi * self.radius

    @property
    def general_coefficients(self) -> Tuple[float, float, float]:
        """D, E, F katsayılarını döndürür: x² + y² + Dx + Ey + F = 0"""
        D = -2.0 * self.center.x
        E = -2.0 * self.center.y
        F = self.center.x ** 2 + self.center.y ** 2 - self.radius ** 2
        return (D, E, F)

    def contains_point(self, point: Point2D) -> str:
        """Noktanın çembere göre konumu: 'inside', 'on_circle', 'outside'"""
        d = self.center.distance_to(point)
        if math.isclose(d, self.radius, abs_tol=1e-7):
            return "on_circle"
        elif d < self.radius:
            return "inside"
        else:
            return "outside"

    def relative_position_with_line(self, line: Line2D) -> str:
        """
        Doğru ile çemberin birbirine göre durumu:
        d < r: 'secant' (kesen - 2 ortak nokta)
        d == r: 'tangent' (teğet - 1 ortak nokta)
        d > r: 'disjoint' (kesişmez - 0 ortak nokta)
        """
        d = line.distance_from_point(self.center)
        if math.isclose(d, self.radius, abs_tol=1e-7):
            return "tangent"
        elif d < self.radius:
            return "secant"
        else:
            return "disjoint"

    def tangent_at_point(self, point: Point2D) -> Line2D:
        """Çember üzerindeki bir noktadan çizilen teğet doğrusunun denklemi."""
        if self.contains_point(point) != "on_circle":
            raise ValueError(f"Nokta {point} çember üzerinde değildir!")
        # Yarıçap vektörü: (point.x - center.x, point.y - center.y) normal vektörüdür.
        A = point.x - self.center.x
        B = point.y - self.center.y
        C = -(A * point.x + B * point.y)
        return Line2D(A, B, C)

    def __repr__(self) -> str:
        return f"Circle2D(center={self.center}, r={self.radius:g})"


class Vector2D:
    """
    2 Boyutlu Öklid Vektörü: u = (x, y)
    Norm, toplama, skaler çarpım, nokta çarpımı, açı ve dik izdüşüm işlemleri.
    """

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    @property
    def norm(self) -> float:
        """Vektörün uzunluğu (normu): ||u|| = sqrt(x^2 + y^2)"""
        return math.hypot(self.x, self.y)

    def add(self, other: Vector2D) -> Vector2D:
        """u + v = (u1 + v1, u2 + v2)"""
        return Vector2D(self.x + other.x, self.y + other.y)

    def subtract(self, other: Vector2D) -> Vector2D:
        """u - v = (u1 - v1, u2 - v2)"""
        return Vector2D(self.x - other.x, self.y - other.y)

    def scale(self, k: float) -> Vector2D:
        """k * u = (k*u1, k*u2)"""
        return Vector2D(k * self.x, k * self.y)

    def dot_product(self, other: Vector2D) -> float:
        """
        Nokta (iç) çarpımı: u · v = u1*v1 + u2*v2 (Sonuç daima reel sayıdır).
        """
        return self.x * other.x + self.y * other.y

    def angle_with(self, other: Vector2D) -> float:
        """
        İki vektör arasındaki açı (radyan cinsinden, [0, pi]).
        cos(theta) = (u · v) / (||u|| * ||v||)
        """
        n1, n2 = self.norm, other.norm
        if math.isclose(n1, 0.0, abs_tol=1e-9) or math.isclose(n2, 0.0, abs_tol=1e-9):
            raise ValueError("Sıfır vektörün açısı tanımsızdır.")
        cos_val = self.dot_product(other) / (n1 * n2)
        # Nümerik taşma emniyeti: [-1.0, 1.0]
        cos_val = max(-1.0, min(1.0, cos_val))
        return math.acos(cos_val)

    def angle_deg_with(self, other: Vector2D) -> float:
        """İki vektör arasındaki açı (derece cinsinden, [0°, 180°])."""
        return math.degrees(self.angle_with(other))

    def is_orthogonal_to(self, other: Vector2D) -> bool:
        """Diklik kontrolü: u · v == 0"""
        return math.isclose(self.dot_product(other), 0.0, abs_tol=1e-7)

    def orthogonal_projection_onto(self, other: Vector2D) -> Vector2D:
        """
        u vektörünün other (v) vektörü üzerine dik izdüşüm vektörü:
        proj_v(u) = ((u · v) / ||v||^2) * v
        """
        v_norm_sq = other.norm ** 2
        if math.isclose(v_norm_sq, 0.0, abs_tol=1e-9):
            raise ValueError("Sıfır vektör üzerine izdüşüm yapılamaz.")
        coeff = self.dot_product(other) / v_norm_sq
        return other.scale(coeff)

    def orthogonal_projection_length(self, other: Vector2D) -> float:
        """Dik izdüşüm uzunluğu: |u · v| / ||v||"""
        if math.isclose(other.norm, 0.0, abs_tol=1e-9):
            raise ValueError("Sıfır vektör üzerine izdüşüm yapılamaz.")
        return abs(self.dot_product(other)) / other.norm

    def __repr__(self) -> str:
        return f"Vector2D({self.x:g}, {self.y:g})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return False
        return math.isclose(self.x, other.x, abs_tol=1e-7) and math.isclose(self.y, other.y, abs_tol=1e-7)


def triangle_centroid(p1: Point2D, p2: Point2D, p3: Point2D) -> Point2D:
    """Üçgenin ağırlık merkezi: G((x1+x2+x3)/3, (y1+y2+y3)/3)"""
    return Point2D((p1.x + p2.x + p3.x) / 3.0, (p1.y + p2.y + p3.y) / 3.0)


def triangle_area(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
    """
    Köşe koordinatları verilen üçgenin analitik alanı (Shoelace / Gauss formülü):
    Alan = 0.5 * |x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)|
    """
    val = p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)
    return 0.5 * abs(val)


def solve_analytic_geometry(task: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Analitik geometri problemlerini Sokratik pedagogiye uygun adımlarla çözen motor arayüzü.
    """
    if task == "distance":
        p1 = Point2D(kwargs["x1"], kwargs["y1"])
        p2 = Point2D(kwargs["x2"], kwargs["y2"])
        d = p1.distance_to(p2)
        return {
            "result": d,
            "formula": "d = sqrt((x2 - x1)^2 + (y2 - y1)^2)",
            "steps": [
                f"Apsisler farkı: {p2.x} - {p1.x} = {p2.x - p1.x}",
                f"Ordinatlar farkı: {p2.y} - {p1.y} = {p2.y - p1.y}",
                f"Kareler toplamı: {(p2.x - p1.x)**2 + (p2.y - p1.y)**2}",
                f"Karekök: sqrt({(p2.x - p1.x)**2 + (p2.y - p1.y)**2}) = {d}",
            ],
        }
    elif task == "line_from_points":
        p1 = Point2D(kwargs["x1"], kwargs["y1"])
        p2 = Point2D(kwargs["x2"], kwargs["y2"])
        line = Line2D.from_two_points(p1, p2)
        return {
            "slope": line.slope,
            "angle_deg": line.angle_deg,
            "general_equation": f"{line.A:.3f}x + {line.B:.3f}y + {line.C:.3f} = 0",
        }
    elif task == "vector_dot":
        u = Vector2D(kwargs["u1"], kwargs["u2"])
        v = Vector2D(kwargs["v1"], kwargs["v2"])
        dot = u.dot_product(v)
        angle = u.angle_deg_with(v)
        proj = u.orthogonal_projection_onto(v)
        return {
            "dot_product": dot,
            "angle_deg": angle,
            "is_orthogonal": u.is_orthogonal_to(v),
            "projection_vector": (proj.x, proj.y),
        }
    elif task == "circle_line":
        c = Circle2D(Point2D(kwargs["cx"], kwargs["cy"]), kwargs["r"])
        line = Line2D(kwargs["A"], kwargs["B"], kwargs["C"])
        pos = c.relative_position_with_line(line)
        d = line.distance_from_point(c.center)
        return {
            "distance_to_center": d,
            "radius": c.radius,
            "relative_position": pos,
        }
    raise ValueError(f"Bilinmeyen analitik geometri görevi: {task}")
