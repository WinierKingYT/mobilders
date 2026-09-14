import uuid
from typing import Dict, Any
from app.root_pedagogy.models import SandboxSessionRequest, SandboxSessionResponse


class InSituRemediationSandbox:
    """
    Mikro-Kum Havuzu (In-Situ Remediation Sandbox).
    Öğrenci lise sorusu çözerken temel bir kuralda takılırsa,
    ana soruyu dondurur, yan tarafta 45 saniyelik görsel kum havuzu açar,
    kavramı pekiştirip öğrenciyi ana soruya geri döndürür.
    """

    def create_sandbox(self, request: SandboxSessionRequest) -> SandboxSessionResponse:
        s_id = str(uuid.uuid4())[:8]
        node = request.root_node_id

        # Hangi görsel araca yönlendirelim?
        if node in ["N_ROOT_01", "N_ROOT_02", "N_ROOT_03", "N_ROOT_04"]:
            tool_type = "NUMBER_LINE"
            instruction = "Sayı doğrusunda başlangıç noktasına git ve işlemi adım adım yürüyerek tamamla."
            action = {"start": -6, "delta": -5, "target": -11}
        elif node in ["N_ROOT_05", "N_ROOT_06", "N_ROOT_07"]:
            tool_type = "PIE_FRACTION"
            instruction = "Farklı dilimlerdeki pizzaları aynı ortak paydada birleştir."
            action = {"fraction1": "1/2", "fraction2": "1/3", "common_denom": 6}
        else:
            tool_type = "BALANCE_SCALE"
            instruction = "Terazinin her iki kefesinden de aynı miktarı alarak x kutusunu yalnız bırak."
            action = {"left_pan": "2x + 3", "right_pan": "11", "remove_weight": 3}

        return SandboxSessionResponse(
            sandbox_id=s_id,
            root_node_id=node,
            tool_type=tool_type,
            instruction=instruction,
            expected_action=action,
            is_resolved=False,
        )

    def verify_action(self, sandbox_id: str, tool_type: str, user_value: Any) -> bool:
        """Kullanıcının kum havuzundaki interaktif eylemini doğrular."""
        if tool_type == "NUMBER_LINE":
            return user_value == -11 or user_value == "-11"
        elif tool_type == "PIE_FRACTION":
            return user_value == 6 or user_value == "5/6" or user_value == "6"
        elif tool_type == "BALANCE_SCALE":
            return user_value == 3 or user_value == "3" or user_value == 4
        return True
