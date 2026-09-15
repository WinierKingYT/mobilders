import 'package:flutter/material.dart';
import '../../../../core/services/haptic_feedback_service.dart';
import '../../../core/app_theme.dart';

class StepSourceLineage {
  final String targetToken;
  final String operation;
  final String originFormula;
  final String explanation;

  const StepSourceLineage({
    required this.targetToken,
    required this.operation,
    required this.originFormula,
    required this.explanation,
  });

  /// Client-side instantaneous derivation resolver matching Core-Engine SourceUnpackerService
  static StepSourceLineage deriveLineage({
    required String currentStep,
    required String previousStep,
    String? selectedToken,
  }) {
    final curr = currentStep.trim();
    final prev = previousStep.trim();

    // 1. Division: 2x = 8 -> x = 4
    final divRegex = RegExp(r'^(\d+)x\s*=\s*(\d+)$');
    final matchDiv = divRegex.firstMatch(prev);
    if (matchDiv != null) {
      final coeff = int.tryParse(matchDiv.group(1) ?? '') ?? 1;
      final rhs = int.tryParse(matchDiv.group(2) ?? '') ?? 0;
      if (coeff != 0 && rhs % coeff == 0) {
        final quotient = rhs ~/ coeff;
        return StepSourceLineage(
          targetToken: '$quotient',
          operation: 'BÖLME (÷)',
          originFormula: '$rhs ÷ $coeff',
          explanation: '$rhs sayısı $coeff\'ye bölünerek $quotient elde edildi.',
        );
      }
    }

    // 2. Addition / Subtraction constant transfer: 2x + 6 = 14 -> 2x = 8
    final addRegex = RegExp(r'[a-zA-Z0-9^]+\s*([+-])\s*(\d+)\s*=\s*(\d+)');
    final matchAdd = addRegex.firstMatch(prev);
    if (matchAdd != null) {
      final sign = matchAdd.group(1);
      final constVal = int.tryParse(matchAdd.group(2) ?? '') ?? 0;
      final prevRhs = int.tryParse(matchAdd.group(3) ?? '') ?? 0;

      if (sign == '+') {
        final res = prevRhs - constVal;
        return StepSourceLineage(
          targetToken: '$res',
          operation: 'ÇIKARMA (-)',
          originFormula: '$prevRhs - $constVal',
          explanation: '$constVal sayısı karşıya eksi geçerek $prevRhs - $constVal = $res oldu.',
        );
      } else if (sign == '-') {
        final res = prevRhs + constVal;
        return StepSourceLineage(
          targetToken: '$res',
          operation: 'TOPLAMA (+)',
          originFormula: '$prevRhs + $constVal',
          explanation: '$constVal sayısı karşıya artı geçerek $prevRhs + $constVal = $res oldu.',
        );
      }
    }

    // 3. Parenthesis expansion: 3(x + 4) -> 3x + 12
    final parenRegex = RegExp(r'(\d+)\s*\(\s*([a-zA-Z]+)\s*([+-])\s*(\d+)\s*\)');
    final matchParen = parenRegex.firstMatch(prev);
    if (matchParen != null) {
      final outside = int.tryParse(matchParen.group(1) ?? '') ?? 1;
      final insideNum = int.tryParse(matchParen.group(4) ?? '') ?? 0;
      final product = outside * insideNum;
      return StepSourceLineage(
        targetToken: '$product',
        operation: 'DAĞILMA ÇARPMASI (×)',
        originFormula: '$outside × $insideNum',
        explanation: 'Dıştaki $outside çarpanı parantez içindeki $insideNum ile çarpılarak $product oldu.',
      );
    }

    // Generic fallback
    return StepSourceLineage(
      targetToken: curr,
      operation: 'CEBİRSEL DÖNÜŞÜM',
      originFormula: 'Önceki: $prev',
      explanation: 'Bu ifade önceki adımdaki \'$prev\' bağıntısının doğrudan sadeleştirilmesidir.',
    );
  }
}

/// Source Unpacker Widget ("Nereden Geldi Bu?")
/// Bölüm 1 - Bilişsel Öğretim Manifestosu.
/// Displays step provenance, origin equations, and friendly lineage explanations.
class SourceUnpackerWidget extends StatefulWidget {
  final String currentStep;
  final String previousStep;
  final String? initialToken;

  const SourceUnpackerWidget({
    super.key,
    required this.currentStep,
    required this.previousStep,
    this.initialToken,
  });

  @override
  State<SourceUnpackerWidget> createState() => _SourceUnpackerWidgetState();
}

class _SourceUnpackerWidgetState extends State<SourceUnpackerWidget> {
  bool _isExpanded = false;
  late StepSourceLineage _lineage;

  @override
  void initState() {
    super.initState();
    _lineage = StepSourceLineage.deriveLineage(
      currentStep: widget.currentStep,
      previousStep: widget.previousStep,
      selectedToken: widget.initialToken,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A).withValues(alpha: 0.70),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: const Color(0xFF38BDF8).withValues(alpha: 0.35),
          width: 1.0,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Toggle Header Button
          InkWell(
            key: const Key('source_unpacker_toggle'),
            borderRadius: BorderRadius.circular(10),
            onTap: () {
              HapticFeedbackService().selectionClick();
              setState(() {
                _isExpanded = !_isExpanded;
              });
            },
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(
                children: [
                  const Icon(
                    Icons.account_tree_outlined,
                    size: 16,
                    color: Color(0xFF38BDF8),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Nereden Geldi Bu?',
                    style: TextStyle(
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF38BDF8),
                      letterSpacing: 0.3,
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    _isExpanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                    size: 18,
                    color: const Color(0xFF94A3B8),
                  ),
                ],
              ),
            ),
          ),

          // Expanded Provenance Card
          if (_isExpanded)
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 10),
              child: Column(
                key: const Key('source_unpacker_content'),
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Divider(height: 1, color: Color(0xFF1E293B)),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: const Color(0xFF38BDF8).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          _lineage.operation,
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF38BDF8),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Köken: ${_lineage.originFormula}',
                        style: const TextStyle(
                          fontFamily: 'monospace',
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFFF1F5F9),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _lineage.explanation,
                    key: const Key('source_unpacker_explanation'),
                    style: const TextStyle(
                      fontSize: 12.5,
                      color: Color(0xFFCBD5E1),
                      height: 1.35,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
