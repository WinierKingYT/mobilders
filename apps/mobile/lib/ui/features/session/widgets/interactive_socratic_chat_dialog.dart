import 'package:flutter/material.dart';
import '../../../core/app_theme.dart';
import 'package:personal_learning_engine/core/services/haptic_feedback_service.dart';
import 'package:personal_learning_engine/data/services/engine_api_service.dart';
import 'package:personal_learning_engine/domain/models/diagnostic_bug.dart';

class SocraticChatMessage {
  final String role; // 'assistant' or 'user'
  final String content;
  final DateTime timestamp;

  const SocraticChatMessage({
    required this.role,
    required this.content,
    required this.timestamp,
  });

  bool get isAssistant => role == 'assistant';
}

/// Interactive, multi-turn Socratic AI Tutor Dialog.
/// Guides the student towards self-discovering the correct algebraic reasoning
/// without ever giving away the final solution roots.
class InteractiveSocraticChatDialog extends StatefulWidget {
  final String targetEquation;
  final DiagnosticBug? diagnosticBug;
  final String? userExpression;
  final Function(String correctedExpression)? onApplyCorrectedStep;
  final EngineApiService? apiService;

  const InteractiveSocraticChatDialog({
    super.key,
    required this.targetEquation,
    this.diagnosticBug,
    this.userExpression,
    this.onApplyCorrectedStep,
    this.apiService,
  });

  static Future<void> show(
    BuildContext context, {
    required String targetEquation,
    DiagnosticBug? diagnosticBug,
    String? userExpression,
    Function(String correctedExpression)? onApplyCorrectedStep,
    EngineApiService? apiService,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => InteractiveSocraticChatDialog(
        targetEquation: targetEquation,
        diagnosticBug: diagnosticBug,
        userExpression: userExpression,
        onApplyCorrectedStep: onApplyCorrectedStep,
        apiService: apiService,
      ),
    );
  }

  @override
  State<InteractiveSocraticChatDialog> createState() => _InteractiveSocraticChatDialogState();
}

class _InteractiveSocraticChatDialogState extends State<InteractiveSocraticChatDialog> {
  final List<SocraticChatMessage> _messages = [];
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;
  late final EngineApiService _api;

  final List<String> _quickChips = const [
    "Neden öyle?",
    "Nasıl yani?",
    "Bir ipucu daha ver",
    "Doğru mu gidiyorum?",
  ];

  @override
  void initState() {
    super.initState();
    _api = widget.apiService ?? EngineApiService();
    _initDialogue();
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _initDialogue() async {
    setState(() => _isLoading = true);

    final bug = widget.diagnosticBug;
    final userExpr = widget.userExpression ?? widget.targetEquation;

    final bugMap = bug != null
        ? {
            'bug_id': bug.bugId,
            'severity': bug.severity,
            'category': bug.category,
            'description': bug.description,
            'remediation_directive': bug.remediationDirective,
            if (bug.offendingTerm != null) 'offending_term': bug.offendingTerm,
          }
        : null;

    final res = await _api.requestSocraticGuidance(
      userInput: userExpr,
      targetEquation: widget.targetEquation,
      diagnosticBug: bugMap,
      conversationHistory: [],
    );

    if (mounted) {
      final text = res['final_output'] as String? ??
          (bug != null ? bug.remediationDirective : "Bu adımı birlikte inceleyelim mi?");

      setState(() {
        _messages.add(SocraticChatMessage(
          role: 'assistant',
          content: text,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
      _scrollToBottom();
    }
  }

  void _sendMessage(String text) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || _isLoading) return;

    HapticFeedbackService().selectionClick();

    _textController.clear();
    setState(() {
      _messages.add(SocraticChatMessage(
        role: 'user',
        content: trimmed,
        timestamp: DateTime.now(),
      ));
      _isLoading = true;
    });
    _scrollToBottom();

    final history = _messages.map((m) => {
      'role': m.role,
      'content': m.content,
    }).toList();

    final bug = widget.diagnosticBug;
    final bugMap = bug != null
        ? {
            'bug_id': bug.bugId,
            'severity': bug.severity,
            'category': bug.category,
            'description': bug.description,
            'remediation_directive': bug.remediationDirective,
            if (bug.offendingTerm != null) 'offending_term': bug.offendingTerm,
          }
        : null;

    final res = await _api.requestSocraticGuidance(
      userInput: trimmed,
      targetEquation: widget.targetEquation,
      diagnosticBug: bugMap,
      conversationHistory: history,
    );

    if (mounted) {
      final reply = res['final_output'] as String? ??
          "Düşünceni adım olarak ifade etmeye ne dersin?";

      setState(() {
        _messages.add(SocraticChatMessage(
          role: 'assistant',
          content: reply,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  bool _isCandidateAlgebraicStep(String text) {
    final t = text.trim();
    return t.contains('=') || t.contains('x') || t.contains('+') || t.contains('-');
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Container(
      height: MediaQuery.of(context).size.height * 0.78,
      margin: EdgeInsets.only(bottom: bottomInset),
      decoration: const BoxDecoration(
        color: Color(0xFF0F172A), // Slate 900
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        border: Border(
          top: BorderSide(color: Color(0xFF38BDF8), width: 2), // Cyan border
        ),
      ),
      child: Column(
        children: [
          // Header Bar
          Container(
            key: const Key('socratic_chat_header'),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: Color(0xFF1E293B))),
            ),
            child: Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: const Color(0xFF0284C7).withValues(alpha: 0.2),
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFF38BDF8)),
                  ),
                  child: const Center(
                    child: Text("🏛️", style: TextStyle(fontSize: 18)),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Sokratik Öğretmen",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        widget.diagnosticBug != null
                            ? widget.diagnosticBug!.description
                            : "Adım Adım Birlikte Keşfedelim",
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  key: const Key('socratic_chat_close_button'),
                  icon: const Icon(Icons.close, color: Colors.white70, size: 20),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
          ),

          // 3-Aşamalı Sokratik İskele Göstergesi
          Container(
            key: const Key('socratic_stage_indicator_bar'),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: const BoxDecoration(
              color: Color(0xFF090D16),
              border: Border(bottom: BorderSide(color: Color(0xFF1E293B))),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildStageChip("1. Empati & Kabul", _messages.length <= 1),
                const Icon(Icons.arrow_forward_ios, size: 10, color: Colors.white24),
                _buildStageChip("2. Somut Sezgi", _messages.length == 2 || _messages.length == 3),
                const Icon(Icons.arrow_forward_ios, size: 10, color: Colors.white24),
                _buildStageChip("3. Kendi Keşfin", _messages.length >= 4),
              ],
            ),
          ),

          // Message List
          Expanded(
            child: ListView.builder(
              key: const Key('socratic_chat_message_list'),
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return _buildMessageBubble(msg);
              },
            ),
          ),

          if (_isLoading)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.4)),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(
                          width: 12,
                          height: 12,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF38BDF8)),
                        ),
                        SizedBox(width: 8),
                        Text(
                          "Sokratik Öğretmen düşünüyor...",
                          style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11, fontStyle: FontStyle.italic),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

          // Quick Suggestion Chips
          Container(
            height: 38,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _quickChips.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, index) {
                final chipText = _quickChips[index];
                return ActionChip(
                  label: Text(chipText, style: const TextStyle(fontSize: 11, color: Color(0xFFE2E8F0))),
                  backgroundColor: const Color(0xFF1E293B),
                  side: const BorderSide(color: Color(0xFF334155)),
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  onPressed: () => _sendMessage(chipText),
                );
              },
            ),
          ),

          const SizedBox(height: 8),

          // Input Bar
          Container(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
            decoration: const BoxDecoration(
              color: Color(0xFF090D16),
              border: Border(top: BorderSide(color: Color(0xFF1E293B))),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    key: const Key('socratic_chat_input'),
                    controller: _textController,
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                    decoration: InputDecoration(
                      hintText: "Düşünceni veya adımını yaz...",
                      hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 13),
                      filled: true,
                      fillColor: const Color(0xFF1E293B),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onSubmitted: _sendMessage,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  key: const Key('socratic_chat_send_button'),
                  icon: const Icon(Icons.send, size: 18),
                  style: IconButton.styleFrom(
                    backgroundColor: const Color(0xFF0284C7),
                    foregroundColor: Colors.white,
                  ),
                  onPressed: () => _sendMessage(_textController.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(SocraticChatMessage msg) {
    final isAssistant = msg.isAssistant;
    final canApply = !isAssistant && _isCandidateAlgebraicStep(msg.content) && widget.onApplyCorrectedStep != null;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: isAssistant ? CrossAxisAlignment.start : CrossAxisAlignment.end,
        children: [
          Row(
            mainAxisAlignment: isAssistant ? MainAxisAlignment.start : MainAxisAlignment.end,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (isAssistant) ...[
                const CircleAvatar(
                  radius: 12,
                  backgroundColor: Color(0xFF0284C7),
                  child: Text("S", style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                ),
                const SizedBox(width: 8),
              ],
              Flexible(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isAssistant ? const Color(0xFF1E293B) : const Color(0xFF0369A1),
                    borderRadius: BorderRadius.circular(12).copyWith(
                      bottomLeft: isAssistant ? Radius.zero : const Radius.circular(12),
                      bottomRight: !isAssistant ? Radius.zero : const Radius.circular(12),
                    ),
                    border: Border.all(
                      color: isAssistant ? const Color(0xFF334155) : const Color(0xFF38BDF8).withValues(alpha: 0.3),
                    ),
                  ),
                  child: Text(
                    msg.content,
                    style: TextStyle(
                      color: isAssistant ? const Color(0xFFF1F5F9) : Colors.white,
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                ),
              ),
            ],
          ),

          // "Bu Adımı Çözüme Aktar" button for student's algebraic insights
          if (canApply)
            Padding(
              padding: const EdgeInsets.only(top: 6, right: 4),
              child: ElevatedButton.icon(
                key: const Key('socratic_apply_step_button'),
                icon: const Icon(Icons.check_circle_outline, size: 14),
                label: const Text("Bu Adımı Çözüme Aktar", style: TextStyle(fontSize: 11)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.accentCorrect,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                onPressed: () {
                  HapticFeedbackService().heavyImpact();
                  widget.onApplyCorrectedStep!(msg.content);
                  Navigator.of(context).pop();
                },
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildStageChip(String title, bool isActive) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isActive ? const Color(0xFF0284C7).withValues(alpha: 0.25) : Colors.transparent,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: isActive ? const Color(0xFF38BDF8) : Colors.white12,
        ),
      ),
      child: Text(
        title,
        style: TextStyle(
          color: isActive ? const Color(0xFF38BDF8) : Colors.white38,
          fontSize: 10,
          fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
}
