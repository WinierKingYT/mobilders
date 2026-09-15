"""
Kişisel Öğrenme Motoru (PLE) - HEDEF 16: Yaşayan Kişisel Matematik Atlası ve Zihin Haritası Gezgini
Tüm Seviyeleri (245 Düğüm: 15 Kök + 230 Çekirdek Müfredat) Birleştiren Bilişsel Atlas Motoru.
Topolojik analiz, darboğaz (bottleneck) tespiti, ZPD sınırı ve 3B/2B uzaysal koordinat projeksiyonu.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple

from app.graph.knowledge_dag import KnowledgeDAG, KnowledgeNode
from app.root_pedagogy.root_dag import RootPrerequisiteDAG, RootNode


class DomainCluster:
    ROOT = "Temel Kökler & Sezgi"
    ALGEBRA = "Cebir & Polinomlar"
    FUNCTIONS_TRIG = "Trigonometri & Fonksiyonlar"
    CALCULUS_DIFF = "Diferansiyel Analiz (Türev)"
    CALCULUS_INT = "İntegral Analizi"
    ANALYTIC_GEOM = "Analitik Geometri & Vektörler"
    EUCLIDEAN_GEOM = "Sentetik Öklid Geometrisi"
    PROB_STATS = "Kombinatorik & Olasılık"
    LOGIC_PROOF = "Mantık & Matematiksel İspat"


@dataclass
class AtlasNode:
    id: str
    canonical_code: str
    title: str
    domain: str
    level: int
    strict_prereqs: List[str]
    description: str
    difficulty: float
    discrimination: float
    # 3D Uzaysal Koordinatlar (Görselleştirme için)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, AtlasNode) and self.id == other.id


class LivingKnowledgeAtlasEngine:
    """
    246 Düğümlü yaşayan matematik atlasını yöneten analitik motor.
    """

    def __init__(self):
        self.nodes: Dict[str, AtlasNode] = {}
        self._load_all_nodes()
        self._compute_3d_spatial_coordinates()

    def _determine_domain(self, node_id: str, level: int) -> str:
        if node_id.startswith("N_ROOT"):
            return DomainCluster.ROOT
        try:
            num = int(node_id[1:])
            if num <= 50:
                return DomainCluster.ALGEBRA
            if num <= 80:
                return DomainCluster.FUNCTIONS_TRIG
            if num <= 110:
                return DomainCluster.CALCULUS_DIFF
            if num <= 135:
                return DomainCluster.CALCULUS_INT
            if num <= 160:
                return DomainCluster.ANALYTIC_GEOM
            if num <= 185:
                return DomainCluster.EUCLIDEAN_GEOM
            if num <= 210:
                return DomainCluster.PROB_STATS
            return DomainCluster.LOGIC_PROOF
        except ValueError:
            return DomainCluster.ALGEBRA

    def _load_all_nodes(self) -> None:
        # 1. 16 Kök Düğümü Yükle (N_ROOT_01 - N_ROOT_16)
        root_dag = RootPrerequisiteDAG()
        for r_id, r_node in root_dag.nodes.items():
            self.nodes[r_id] = AtlasNode(
                id=r_id,
                canonical_code=r_node.canonical_code,
                title=r_node.title,
                domain=DomainCluster.ROOT,
                level=int(r_node.level),
                strict_prereqs=r_node.strict_prereqs,
                description=r_node.description,
                difficulty=getattr(r_node, "difficulty", float(r_node.level)),
                discrimination=1.5,
            )

        # 2. 230 Müfredat Düğümünü Yükle (N01 - N230)
        core_dag = KnowledgeDAG()
        for c_id, c_node in core_dag.nodes.items():
            domain = self._determine_domain(c_id, c_node.level)
            self.nodes[c_id] = AtlasNode(
                id=c_id,
                canonical_code=c_node.canonical_code,
                title=c_node.title,
                domain=domain,
                level=c_node.level,
                strict_prereqs=c_node.strict_prereqs,
                description=c_node.description,
                difficulty=c_node.default_difficulty_b,
                discrimination=c_node.discrimination_a,
            )

    def _compute_3d_spatial_coordinates(self) -> None:
        """
        Düğümlerin 3B uzaydaki (x, y, z) koordinatlarını hesaplar:
        - z ekseni: Bilişsel Seviye hiyerarşisi (-3 ile +19 arası)
        - x, y düzlemi: Alan kümesine göre açısal radyal dağılım + düğüm içi indeks
        """
        domain_angles = {
            DomainCluster.ROOT: 0.0,
            DomainCluster.ALGEBRA: math.pi / 4,
            DomainCluster.FUNCTIONS_TRIG: math.pi / 2,
            DomainCluster.CALCULUS_DIFF: 3 * math.pi / 4,
            DomainCluster.CALCULUS_INT: math.pi,
            DomainCluster.ANALYTIC_GEOM: 5 * math.pi / 4,
            DomainCluster.EUCLIDEAN_GEOM: 3 * math.pi / 2,
            DomainCluster.PROB_STATS: 7 * math.pi / 4,
            DomainCluster.LOGIC_PROOF: 2 * math.pi,
        }

        domain_counters: Dict[str, int] = {d: 0 for d in domain_angles}

        for node_id, node in sorted(self.nodes.items(), key=lambda item: (item[1].level, item[0])):
            base_angle = domain_angles.get(node.domain, 0.0)
            idx = domain_counters[node.domain]
            domain_counters[node.domain] += 1

            # z: seviyeye göre dikey katman
            node.z = float(node.level * 40.0)

            # x, y: radyal genişlik
            radius = 120.0 + (idx % 5) * 25.0
            angle = base_angle + (idx * 0.12)
            node.x = round(radius * math.cos(angle), 2)
            node.y = round(radius * math.sin(angle), 2)

    # =================================================================
    # ANALİTİK VE TOPOLOJİK GEZGİN API'LERİ
    # =================================================================

    def get_total_nodes(self) -> int:
        return len(self.nodes)

    def get_node(self, node_id: str) -> Optional[AtlasNode]:
        return self.nodes.get(node_id)

    def get_nodes_by_domain(self, domain: str) -> List[AtlasNode]:
        return [node for node in self.nodes.values() if node.domain == domain]

    def get_domain_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for node in self.nodes.values():
            summary[node.domain] = summary.get(node.domain, 0) + 1
        return summary

    def get_recursive_prerequisites(self, node_id: str) -> Set[str]:
        """Bir düğümün geçmişe doğru tüm öncüllerini (ancestors) toplar."""
        node = self.nodes.get(node_id)
        if not node:
            return set()
        prereqs = set(node.strict_prereqs)
        for parent_id in list(prereqs):
            prereqs.update(self.get_recursive_prerequisites(parent_id))
        return prereqs

    def get_downstream_dependents(self, node_id: str) -> Set[str]:
        """Bu düğüme doğrudan veya dolaylı bağlı olan tüm ileri düğümleri (descendants) bulur."""
        dependents: Set[str] = set()
        for other_id, other_node in self.nodes.items():
            if node_id in other_node.strict_prereqs:
                dependents.add(other_id)
                dependents.update(self.get_downstream_dependents(other_id))
        return dependents

    def compute_zpd_frontier(self, mastered_ids: Set[str]) -> List[str]:
        """
        Öğrencinin Yakınsak Gelişim Alanı (ZPD) Sınırını hesaplar:
        Öğrencinin henüz bilmediği, fakat tüm önkoşullarını bildiği hazır düğümler.
        """
        zpd: List[str] = []
        for node_id, node in self.nodes.items():
            if node_id in mastered_ids:
                continue
            if all(p in mastered_ids for p in node.strict_prereqs):
                zpd.append(node_id)
        return sorted(zpd)

    def find_critical_bottlenecks(self, mastered_ids: Set[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Bilişsel Darboğaz Analizi:
        Henüz öğrenilmemiş olan ve arkasında en çok kilitli düğüm tutan kritik kök düğümleri tespit eder.
        """
        candidates: List[Tuple[str, int]] = []
        for node_id, node in self.nodes.items():
            if node_id in mastered_ids:
                continue
            # Bu düğüm öğrenilirse açılacak potansiyel alt ağacın boyutu
            blocked_count = len(self.get_downstream_dependents(node_id))
            candidates.append((node_id, blocked_count))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top_bottlenecks = candidates[:top_k]

        return [
            {
                "node_id": c[0],
                "title": self.nodes[c[0]].title,
                "domain": self.nodes[c[0]].domain,
                "blocked_dependents_count": c[1],
            }
            for c in top_bottlenecks
        ]

    def calculate_curriculum_progress(self, mastered_ids: Set[str]) -> Dict[str, Any]:
        """Genel ve alan bazlı müfredat tamamlama oranlarını hesaplar."""
        total = len(self.nodes)
        mastered_valid = mastered_ids.intersection(self.nodes.keys())
        overall_pct = (len(mastered_valid) / total) * 100.0 if total > 0 else 0.0

        domain_stats: Dict[str, Dict[str, Any]] = {}
        for domain, count in self.get_domain_summary().items():
            domain_nodes = self.get_nodes_by_domain(domain)
            mastered_in_domain = len([n for n in domain_nodes if n.id in mastered_valid])
            pct = (mastered_in_domain / count) * 100.0 if count > 0 else 0.0
            domain_stats[domain] = {
                "total": count,
                "mastered": mastered_in_domain,
                "percentage": round(pct, 1),
            }

        return {
            "total_nodes": total,
            "mastered_count": len(mastered_valid),
            "overall_percentage": round(overall_pct, 1),
            "domain_stats": domain_stats,
        }

    def generate_atlas_payload(self, mastered_ids: Set[str]) -> Dict[str, Any]:
        """
        Mobil istemci ve 3B Atlas Gezgini için eksiksiz seri hale getirilmiş graf verisi üretir.
        """
        zpd_set = set(self.compute_zpd_frontier(mastered_ids))
        nodes_payload = []
        edges_payload = []

        for node_id, node in self.nodes.items():
            if node_id in mastered_ids:
                status = "MASTERED"
            elif node_id in zpd_set:
                status = "IN_ZPD"
            else:
                status = "LOCKED"

            nodes_payload.append({
                "id": node.id,
                "title": node.title,
                "domain": node.domain,
                "level": node.level,
                "difficulty": node.difficulty,
                "status": status,
                "x": node.x,
                "y": node.y,
                "z": node.z,
                "prereq_count": len(node.strict_prereqs),
            })

            for p_id in node.strict_prereqs:
                if p_id in self.nodes:
                    edges_payload.append({
                        "source": p_id,
                        "target": node.id,
                        "active": p_id in mastered_ids,
                    })

        return {
            "meta": {
                "total_nodes": len(self.nodes),
                "total_edges": len(edges_payload),
                "mastered_count": len(mastered_ids.intersection(self.nodes.keys())),
                "zpd_count": len(zpd_set),
            },
            "nodes": nodes_payload,
            "edges": edges_payload,
        }
