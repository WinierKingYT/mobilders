import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../domain/models/solution_step.dart';
import '../../domain/models/diagnostic_item.dart';

class EngineApiService {
  final String baseUrl;
  final http.Client _client;

  EngineApiService({
    String? baseUrl,
    http.Client? client,
  })  : baseUrl = baseUrl ?? _defaultBaseUrl(),
        _client = client ?? http.Client();

  static String _defaultBaseUrl() {
    // Android emulator routes host localhost to 10.0.2.2
    try {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:8000';
      }
    } catch (_) {
      // Non-io or web fallback
    }
    return 'http://127.0.0.1:8000';
  }

  Future<SolutionStep> verifyStep({
    required String sessionId,
    required String nodeId,
    required int stepNumber,
    required String userExpression,
    required String targetEquation,
    String? previousStep,
    int? elapsedMs,
    double? currentPl,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/session/step/verify');
    final payload = {
      'session_id': sessionId,
      'node_id': nodeId,
      'step_number': stepNumber,
      'user_expression': userExpression,
      'target_equation': targetEquation,
      if (previousStep != null) 'previous_step': previousStep,
      if (elapsedMs != null) 'elapsed_ms': elapsedMs,
      if (currentPl != null) 'current_p_l': currentPl,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return SolutionStep.fromJson(
        json,
        stepNumber: stepNumber,
        userExpression: userExpression,
        elapsedMs: elapsedMs ?? 0,
      );
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<DiagnosticItem?> getNextCatItem({
    required String sessionId,
    required double currentTheta,
    required List<String> administeredItemIds,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/diagnostic/next-item');
    final payload = {
      'session_id': sessionId,
      'current_theta': currentTheta,
      'administered_item_ids': administeredItemIds,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (response.statusCode == 200) {
      if (response.body.isEmpty || response.body == 'null') return null;
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return DiagnosticItem.fromJson(json);
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<DiagnosticSubmitResult> submitCatResponse({
    required String sessionId,
    required String itemId,
    required bool isCorrect,
    required List<List<dynamic>> administeredHistory,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/diagnostic/submit');
    final payload = {
      'session_id': sessionId,
      'item_id': itemId,
      'is_correct': isCorrect,
      'administered_history': administeredHistory,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return DiagnosticSubmitResult.fromJson(json);
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  void dispose() {
    _client.close();
  }
}
