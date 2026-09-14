# 25-PROBLEM-AND-ITEM-TEMPLATE-SCHEMA.md
# PROBLEM VE MADDE ŞABLONU VERİ ŞARTNAMESİ (PROBLEM BANK & PARAMETRIC SCHEMA)
## Parametrik Problem Üretimi, Çok Adımlı Çözüm Ağaçları ve JSON Şemaları

---

## 1. GENEL BAKIŞ VE TASARIM PRENSİBİ

Kişisel Öğrenme Motoru, statik soru ezberletmek yerine **sonsuz parametrik varyasyon** ve **katı matematiksel kısıtlar** ile çalışan üretici bir problem havuzu kullanır:

1. **Parametrik Üretim:** Katsayılar ($a, b, c$) rastgele değil, hedef pedagojik amaca uygun olarak tam sayı kökler, rasyonel çözümler veya irrasyonel kökler üretecek kısıtlar altında dinamik olarak çekilir.
2. **Çok Adımlı Kanonik Çözüm Yolu (Multi-Step DAG):** Her problem yalnızca sonuca değil; adım adım takip edilebilen bir ara işlem ağına (`canonical_steps`) sahiptir.
3. **Kabul Edilebilir Eşdeğerlik Varyantları:** Deterministik SymPy AST motoru, terimlerin yer değişimi ($x+3=0$ veya $3+x=0$) veya iki tarafın aynı sayıyla çarpılması gibi meşru cebirsel adımları geçerli kabul eder.

---

## 2. PARAMETRİK PROBLEM ŞABLONU JSON ŞEMASI (`ProblemTemplate`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ProblemTemplate",
  "type": "object",
  "required": [
    "template_id", "target_node_id", "difficulty_level", "expression_pattern",
    "coefficient_constraints", "canonical_solution_path"
  ],
  "properties": {
    "template_id": { "type": "string", "example": "TMPL_QUAD_COMPLETE_SQ_01" },
    "target_node_id": { "type": "string", "example": "N15" },
    "title_tr": { "type": "string", "example": "Tam Kareye Tamamlama Yoluyla Çözüm" },
    "difficulty_level": { "type": "number", "minimum": -3.0, "maximum": 3.0, "example": 0.8 },
    "expression_pattern": { 
      "type": "string", 
      "description": "Parametrik şablon ifadesi",
      "example": "x^2 + {b}x = {c}" 
    },
    "coefficient_constraints": {
      "type": "object",
      "properties": {
        "b": { "type": "string", "description": "Çift tamsayı kuralı: 2 * k, k in [1, 5]", "example": "even_integer(2, 10)" },
        "c": { "type": "string", "description": "Karekökü tam sayı veya rasyonel çıkacak sabit", "example": "integer(1, 15)" },
        "discriminant_check": { "type": "string", "example": "(b/2)^2 + c > 0" }
      }
    },
    "canonical_solution_path": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["step_index", "pedagogical_goal", "expected_canonical_form"],
        "properties": {
          "step_index": { "type": "integer", "minimum": 1 },
          "pedagogical_goal": { "type": "string" },
          "expected_canonical_form": { "type": "string" },
          "allowed_ast_equivalents": { "type": "array", "items": { "type": "string" } },
          "targeted_buggy_rules": { "type": "array", "items": { "type": "string" } }
        }
      }
    }
  }
}
```

---

## 3. SOMUT ŞABLON ÖRNEĞİ: TAM KAREYE TAMAMLAMA (`TMPL_QUAD_COMPLETE_SQ_01`)

```json
{
  "template_id": "TMPL_QUAD_COMPLETE_SQ_01",
  "target_node_id": "N15",
  "title_tr": "Tam Kareye Tamamlama (b Çift, Monik)",
  "difficulty_level": 0.80,
  "expression_pattern": "x^2 + 6x = 2",
  "coefficient_constraints": {
    "a": 1,
    "b": 6,
    "c": 2
  },
  "canonical_solution_path": [
    {
      "step_index": 1,
      "pedagogical_goal": "Her iki tarafa (b/2)^2 = 9 ekleyerek sol tarafı tam kare yapmak",
      "expected_canonical_form": "x^2 + 6*x + 9 = 11",
      "allowed_ast_equivalents": [
        "x**2 + 6*x + 9 = 11",
        "(x + 3)**2 = 11",
        "9 + 6*x + x**2 = 11"
      ],
      "targeted_buggy_rules": ["BUG-QUAD-07", "BUG-QUAD-03"]
    },
    {
      "step_index": 2,
      "pedagogical_goal": "Sol tarafı parantez karesi olarak yazmak",
      "expected_canonical_form": "(x + 3)^2 = 11",
      "allowed_ast_equivalents": [
        "(x + 3)**2 = 11",
        "(3 + x)**2 = 11"
      ],
      "targeted_buggy_rules": ["BUG-QUAD-03"]
    },
    {
      "step_index": 3,
      "pedagogical_goal": "Her iki tarafın karekökünü alarak mutlak değerli/artı-eksi kökleri açığa çıkarmak",
      "expected_canonical_form": "x + 3 = \\pm \\sqrt{11}",
      "allowed_ast_equivalents": [
        "x + 3 = sqrt(11) \\lor x + 3 = -sqrt(11)",
        "Abs(x + 3) = sqrt(11)"
      ],
      "targeted_buggy_rules": ["BUG-QUAD-02"]
    },
    {
      "step_index": 4,
      "pedagogical_goal": "x'i yalnız bırakarak kökleri elde etmek",
      "expected_canonical_form": "x = -3 \\pm \\sqrt{11}",
      "allowed_ast_equivalents": [
        "x = -3 + sqrt(11) \\lor x = -3 - sqrt(11)",
        "x = sqrt(11) - 3 \\lor x = -sqrt(11) - 3"
      ],
      "targeted_buggy_rules": ["BUG-QUAD-06"]
    }
  ]
}
```

---

## 4. DİNAMİK PROBLEM ÜRETİCİSİ ÇALIŞMA PROTOKOLÜ

```text
[ ZPD Termostatı Hedef Düğümü Belirler: N15 ]
                   │
                   ▼
[ ProblemGenerator: N15 Şablonunu Yükler ]
  - b için [2, 4, 6, 8] arasından rastgele seçim yapar (Örn: b = 6).
  - Sabit terim için uygun c seçer (Örn: c = 2).
  - SymPy ile çözümü ve ara adımları derler.
                   │
                   ▼
[ İstemciye Problem Yükü Aktarılır (WebSocket/REST) ]
  - Soru Metni: "x² + 6x = 2 denklemini tam kareye tamamlama yöntemiyle çözünüz."
  - İskele Seviyesi: 1 (Minimal İpucu).
```
