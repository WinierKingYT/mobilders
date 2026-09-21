import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../../core/localization.dart';
import '../../../../../core/services/haptic_feedback_service.dart';
import '../../view_models/session_view_model.dart';
import '../../../touchpad/math_touchpad.dart';

void showSessionSettingsModal(BuildContext context) {
  showModalBottomSheet(
    context: context,
    backgroundColor: const Color(0xFF0F172A),
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
    ),
    builder: (ctx) {
      return Consumer<SessionViewModel>(
        builder: (context, sessionVm, _) {
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.tune_rounded, color: Color(0xFF38BDF8)),
                      const SizedBox(width: 8),
                      const Expanded(
                        child: Text(
                          "Erişilebilirlik & Müfredat Ayarları",
                          style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white60, size: 20),
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                  const Divider(color: Color(0xFF1E293B)),

                  // ADHD Tunnel Focus Mode Toggle
                  SwitchListTile(
                    value: sessionVm.isTunnelFocusMode,
                    activeThumbColor: const Color(0xFF38BDF8),
                    title: const Text("DEHB Tünel Odak Modu", style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                    subtitle: const Text("Obsidyen siyahı ve yüksek kontrast ile dikkat dağıtıcıları sıfırlar.", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                    onChanged: (_) {
                      HapticFeedbackService().selectionClick();
                      sessionVm.toggleTunnelFocusMode();
                    },
                  ),

                  // Dyscalculia Visual Aids Toggle
                  SwitchListTile(
                    value: sessionVm.isDyscalculiaHelper,
                    activeThumbColor: const Color(0xFF10B981),
                    title: const Text("Diskalkuli Görsel Desteği", style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                    subtitle: const Text("Uzamsal sayı çizgisi ve renk kodlu cebirsel terim rozetleri.", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                    onChanged: (_) {
                      HapticFeedbackService().selectionClick();
                      sessionVm.toggleDyscalculiaHelper();
                    },
                  ),

                  const SizedBox(height: 12),
                  const Text("Girdi Modu & Çizim Tuvali", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _buildInputModeOption(
                        label: "Touchpad",
                        icon: Icons.grid_view_rounded,
                        mode: InputMode.touchpad,
                        selectedMode: sessionVm.inputMode,
                        onSelect: () {
                          HapticFeedbackService().modeSwitch();
                          sessionVm.setInputMode(InputMode.touchpad);
                        },
                      ),
                      const SizedBox(width: 8),
                      _buildInputModeOption(
                        label: "Klavye",
                        icon: Icons.keyboard_outlined,
                        mode: InputMode.virtualKeyboard,
                        selectedMode: sessionVm.inputMode,
                        onSelect: () {
                          HapticFeedbackService().modeSwitch();
                          sessionVm.setInputMode(InputMode.virtualKeyboard);
                        },
                      ),
                      const SizedBox(width: 8),
                      _buildInputModeOption(
                        label: "Çizim (İnk)",
                        icon: Icons.draw_rounded,
                        mode: InputMode.inkingCanvas,
                        selectedMode: sessionVm.inputMode,
                        onSelect: () {
                          HapticFeedbackService().modeSwitch();
                          sessionVm.setInputMode(InputMode.inkingCanvas);
                        },
                      ),
                    ],
                  ),

                  const SizedBox(height: 12),
                  const Text("Müfredat Standardı", style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),

                  // Curriculum Standard Dropdown
                  StatefulBuilder(
                    builder: (context, setStateDropdown) {
                      return Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: DropdownButton<CurriculumType>(
                          value: AppLocalization.currentCurriculum,
                          dropdownColor: const Color(0xFF1E293B),
                          isExpanded: true,
                          underline: const SizedBox(),
                          style: const TextStyle(color: Colors.white, fontSize: 13),
                          items: CurriculumType.values.map((type) {
                            return DropdownMenuItem<CurriculumType>(
                              value: type,
                              child: Text(type.displayName),
                            );
                          }).toList(),
                          onChanged: (newType) {
                            if (newType != null) {
                              setStateDropdown(() {
                                AppLocalization.setCurriculum(newType);
                              });
                            }
                          },
                        ),
                      );
                    },
                  ),

                  const SizedBox(height: 16),
                  // Offline Queue Status
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          sessionVm.pendingOfflineCount > 0 ? Icons.cloud_off : Icons.cloud_done,
                          color: sessionVm.pendingOfflineCount > 0 ? const Color(0xFFF59E0B) : const Color(0xFF10B981),
                          size: 20,
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            sessionVm.pendingOfflineCount > 0
                                ? "${sessionVm.pendingOfflineCount} adım çevrimdışı kuyrukta bekliyor"
                                : "Tüm adımlar bulutla senkronize",
                            style: const TextStyle(color: Colors.white70, fontSize: 12),
                          ),
                        ),
                        if (sessionVm.pendingOfflineCount > 0)
                          TextButton(
                            onPressed: () => sessionVm.syncPendingOfflineSteps(),
                            child: const Text("Eşzamanla", style: TextStyle(color: Color(0xFF38BDF8), fontSize: 12)),
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                ],
              ),
            ),
          );
        },
      );
    },
  );
}

Widget _buildInputModeOption({
  required String label,
  required IconData icon,
  required InputMode mode,
  required InputMode selectedMode,
  required VoidCallback onSelect,
}) {
  final isSelected = mode == selectedMode;
  return Expanded(
    child: InkWell(
      borderRadius: BorderRadius.circular(8),
      onTap: onSelect,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF38BDF8).withValues(alpha: 0.2) : const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF334155),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Column(
          children: [
            Icon(icon, size: 18, color: isSelected ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8)),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                color: isSelected ? Colors.white : const Color(0xFF94A3B8),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}
