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
    // 127.0.0.1 routes correctly via adb reverse on Android and localhost on desktop/web
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
    String? clientMsgId,
    DateTime? clientTimestamp,
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
      if (clientMsgId != null) 'client_msg_id': clientMsgId,
      if (clientTimestamp != null) 'client_timestamp': clientTimestamp.toIso8601String(),
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

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

  Future<Map<String, dynamic>> replayOfflineBatch({
    required String sessionId,
    required List<Map<String, dynamic>> events,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/session/replay-queue');
    final payload = {
      'session_id': sessionId,
      'events': events,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
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
    ).timeout(const Duration(seconds: 4));

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
    ).timeout(const Duration(seconds: 4));

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

  Future<Map<String, dynamic>> scanAndDiagnoseNotebook({
    String? imageBase64,
    String? rawTextOverride,
    String? targetProblem,
    String? studentId,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/scan/diagnose');
    final payload = {
      if (imageBase64 != null) 'image_base64': imageBase64,
      if (rawTextOverride != null) 'raw_text_override': rawTextOverride,
      if (targetProblem != null) 'target_problem': targetProblem,
      'student_id': studentId ?? 'STU-SCAN-01',
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchModelingProblems() async {
    final uri = Uri.parse('$baseUrl/api/v1/modeling/problems');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> fetchModelingProblem(String problemId) async {
    final uri = Uri.parse('$baseUrl/api/v1/modeling/problem/$problemId');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitModelingScaffoldStep({
    required String sessionId,
    required String problemId,
    required String stage,
    required String studentInput,
    String? variableName,
    String? studentId,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/modeling/scaffold/step');
    final payload = {
      'session_id': sessionId,
      'problem_id': problemId,
      'stage': stage,
      'student_input': studentInput,
      'variable_name': variableName ?? 'x',
      'student_id': studentId ?? 'STU-MODEL-01',
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> solveAnalyticGeometry({
    required String task,
    required Map<String, dynamic> params,
    String? studentId,
    String? problemStatement,
    String? studentStep,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/geometry/analytic/solve');
    final payload = {
      'task': task,
      'params': params,
      if (studentId != null) 'student_id': studentId,
      if (problemStatement != null) 'problem_statement': problemStatement,
      if (studentStep != null) 'student_step': studentStep,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> solveSyntheticGeometry({
    required String task,
    required Map<String, dynamic> params,
    String? studentId,
    String? problemStatement,
    String? studentStep,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/geometry/synthetic/solve');
    final payload = {
      'task': task,
      'params': params,
      if (studentId != null) 'student_id': studentId,
      if (problemStatement != null) 'problem_statement': problemStatement,
      if (studentStep != null) 'student_step': studentStep,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchVaultMistakes(
    String userId, {
    String? status,
  }) async {
    final query = status != null ? '?status=$status' : '';
    final uri = Uri.parse('$baseUrl/api/v1/vault/list/$userId$query');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchDueVaultMistakes(String userId) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/due/$userId');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body) as List<dynamic>;
      return list.map((e) => e as Map<String, dynamic>).toList();
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> fetchVaultAnalytics(String userId) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/analytics/$userId');
    final response = await _client.get(uri).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> recordVaultMistake({
    required String userId,
    required String nodeId,
    required String bugId,
    required String problemStatement,
    required String offendingStep,
    required String correctPrinciple,
    required String remediationDirective,
    double? timestamp,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/record');
    final payload = {
      'user_id': userId,
      'node_id': nodeId,
      'bug_id': bugId,
      'problem_statement': problemStatement,
      'offending_step': offendingStep,
      'correct_principle': correctPrinciple,
      'remediation_directive': remediationDirective,
      if (timestamp != null) 'timestamp': timestamp,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> startSelfCorrection(String mistakeId) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/start');
    final payload = {'mistake_id': mistakeId};

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitSelfCorrectionDiagnosis({
    required String mistakeId,
    required bool isIdentified,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/diagnose');
    final payload = {
      'mistake_id': mistakeId,
      'is_identified': isIdentified,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitSelfCorrectionExplanation({
    required String mistakeId,
    required bool isPrincipleCorrect,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/explain');
    final payload = {
      'mistake_id': mistakeId,
      'is_principle_correct': isPrincipleCorrect,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitSelfCorrectionResolve({
    required String mistakeId,
    required bool isCorrect,
    double? currentTime,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/self-correction/resolve');
    final payload = {
      'mistake_id': mistakeId,
      'is_correct': isCorrect,
      if (currentTime != null) 'current_time': currentTime,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> spawnBossBattle({
    required String userId,
    double? currentTime,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/boss-battle/spawn');
    final payload = {
      'user_id': userId,
      if (currentTime != null) 'current_time': currentTime,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw HttpException(
        'Server returned ${response.statusCode}: ${response.body}',
        uri: uri,
      );
    }
  }

  Future<Map<String, dynamic>> submitBossBattleTurn({
    required String battleId,
    required bool isCleanSolve,
    double? currentTime,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/vault/boss-battle/turn');
    final payload = {
      'battle_id': battleId,
      'is_clean_solve': isCleanSolve,
      if (currentTime != null) 'current_time': currentTime,
    };

    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    ).timeout(const Duration(seconds: 4));

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
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
