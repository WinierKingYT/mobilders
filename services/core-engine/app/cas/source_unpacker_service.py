"""
Source Unpacker Service ("Nereden Geldi Bu?").
Bölüm 1 - Bilişsel Öğretim Manifestosu.
Maps numbers and terms in an algebraic step back to their predecessor origins and operations.
"""

from __future__ import annotations
import re
from typing import Optional
from pydantic import BaseModel


class SourceOrigin(BaseModel):
    target_token: str
    operation: str
    operand_left: str
    operand_right: str
    origin_formula: str
    explanation: str


class SourceUnpackerService:
    """
    Traces the computational lineage of numbers and algebraic tokens between steps.
    """

    @classmethod
    def unpack_token(
        cls,
        current_step: str,
        previous_step: str,
        token: str,
    ) -> Optional[SourceOrigin]:
        curr = current_step.strip()
        prev = previous_step.strip()
        tok = token.strip()

        if not curr or not prev or not tok:
            return None

        # Case 1: Division transition: e.g. 2x = 8 -> x = 4 (token: '4')
        match_prev_mult = re.search(r"(\d+)x\s*=\s*(\d+)", prev)
        if match_prev_mult:
            coeff = int(match_prev_mult.group(1))
            rhs = int(match_prev_mult.group(2))
            if coeff != 0 and rhs % coeff == 0:
                expected_ans = str(rhs // coeff)
                if tok == expected_ans:
                    return SourceOrigin(
                        target_token=tok,
                        operation="DIVISION",
                        operand_left=str(rhs),
                        operand_right=str(coeff),
                        origin_formula=f"{rhs} ÷ {coeff}",
                        explanation=f"{rhs} sayısı {coeff}'ye bölünerek {tok} elde edildi.",
                    )

        # Case 2: Subtraction / constant transfer: e.g. 2x + 6 = 14 -> 2x = 8 (token: '8')
        match_prev_add = re.search(r"[a-zA-Z0-9^]+\s*([+-])\s*(\d+)\s*=\s*(\d+)", prev)
        if match_prev_add:
            sign = match_prev_add.group(1)
            const_val = int(match_prev_add.group(2))
            prev_rhs = int(match_prev_add.group(3))
            if sign == "+":
                result = prev_rhs - const_val
                if tok == str(result):
                    return SourceOrigin(
                        target_token=tok,
                        operation="SUBTRACTION",
                        operand_left=str(prev_rhs),
                        operand_right=str(const_val),
                        origin_formula=f"{prev_rhs} - {const_val}",
                        explanation=f"{const_val} karşıya eksi geçerek {prev_rhs} - {const_val} = {tok} oldu.",
                    )
            elif sign == "-":
                result = prev_rhs + const_val
                if tok == str(result):
                    return SourceOrigin(
                        target_token=tok,
                        operation="ADDITION",
                        operand_left=str(prev_rhs),
                        operand_right=str(const_val),
                        origin_formula=f"{prev_rhs} + {const_val}",
                        explanation=f"{const_val} karşıya artı geçerek {prev_rhs} + {const_val} = {tok} oldu.",
                    )

        # Case 3: Parenthesis expansion: e.g. 3(x + 4) -> 3x + 12 (token: '12' or '3x')
        match_distrib = re.search(r"(\d+)\s*\(\s*([a-zA-Z]+)\s*([+-])\s*(\d+)\s*\)", prev)
        if match_distrib:
            outside = int(match_distrib.group(1))
            var_name = match_distrib.group(2)
            dist_sign = match_distrib.group(3)
            inside_num = int(match_distrib.group(4))

            mult_num = outside * inside_num
            var_term = f"{outside}{var_name}"

            if tok == str(mult_num):
                return SourceOrigin(
                    target_token=tok,
                    operation="MULTIPLICATION",
                    operand_left=str(outside),
                    operand_right=str(inside_num),
                    origin_formula=f"{outside} × {inside_num}",
                    explanation=f"Dıştaki {outside} çarpanı parantez içindeki {inside_num} ile çarpılarak {tok} oldu.",
                )
            if tok == var_term or tok == f"{outside}*{var_name}":
                return SourceOrigin(
                    target_token=tok,
                    operation="EXPANSION",
                    operand_left=str(outside),
                    operand_right=var_name,
                    origin_formula=f"{outside} × {var_name}",
                    explanation=f"Dıştaki {outside} çarpanı {var_name} ile dağıtılarak {tok} terimi oluştu.",
                )

        # Generic token fallback
        return SourceOrigin(
            target_token=tok,
            operation="STEP_DERIVATION",
            operand_left=prev,
            operand_right=tok,
            origin_formula=f"Önceki Adım: {prev}",
            explanation=f"{tok} terimi önceki adım olan '{prev}' ifadesinin cebirsel sadeleştirmesinden türemiştir.",
        )
