import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/focus_domain_models.dart';

/// Exceptions thrown by the Focus API Client.
class FocusApiException implements Exception {
  final String message;
  final int statusCode;
  final String? code;

  const FocusApiException(this.message, {required this.statusCode, this.code});

  @override
  String toString() => 'FocusApiException(HTTP $statusCode, code: $code): $message';
}

class FocusConflictException extends FocusApiException {
  const FocusConflictException(super.message, {String? code})
      : super(statusCode: 409, code: code ?? 'FOCUS_STREAM_CONFLICT');
}

class FocusRateLimitException extends FocusApiException {
  const FocusRateLimitException(super.message, {String? code})
      : super(statusCode: 429, code: code ?? 'FOCUS_RATE_LIMIT_EXCEEDED');
}

class FocusValidationException extends FocusApiException {
  const FocusValidationException(super.message, {String? code})
      : super(statusCode: 422, code: code ?? 'FOCUS_VALIDATION_ERROR');
}

class FocusDisabledException extends FocusApiException {
  const FocusDisabledException(super.message, {String? code})
      : super(statusCode: 503, code: code ?? 'FOCUS_DISABLED');
}

class FocusNotFoundException extends FocusApiException {
  const FocusNotFoundException(super.message, {String? code})
      : super(statusCode: 404, code: code ?? 'FOCUS_EPISODE_NOT_FOUND');
}

/// Robust HTTP client service for the event-sourced MOBILDERS Focus Kernel (/focus/v1).
class FocusApiService {
  final String baseUrl;
  final http.Client _client;
  final String? authToken;

  FocusApiService({
    this.baseUrl = 'http://127.0.0.1:8000/focus/v1',
    http.Client? client,
    this.authToken,
  }) : _client = client ?? http.Client();

  Map<String, String> _buildHeaders({
    String? idempotencyKey,
    int? expectedSequence,
  }) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-Request-ID': 'req_${DateTime.now().microsecondsSinceEpoch}',
    };
    if (authToken != null) {
      headers['Authorization'] = authToken!;
    }
    if (idempotencyKey != null) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    if (expectedSequence != null) {
      headers['X-Focus-Expected-Sequence'] = expectedSequence.toString();
    }
    return headers;
  }

  Never _handleError(http.Response response) {
    String message = response.body;
    String? code;
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        if (decoded['detail'] is Map<String, dynamic>) {
          final detail = decoded['detail'] as Map<String, dynamic>;
          message = detail['message']?.toString() ?? message;
          code = detail['code']?.toString();
        } else if (decoded['detail'] != null) {
          message = decoded['detail'].toString();
        }
      }
    } catch (_) {}

    switch (response.statusCode) {
      case 404:
        throw FocusNotFoundException(message, code: code);
      case 409:
        throw FocusConflictException(message, code: code);
      case 422:
        throw FocusValidationException(message, code: code);
      case 429:
        throw FocusRateLimitException(message, code: code);
      case 503:
        throw FocusDisabledException(message, code: code);
      default:
        throw FocusApiException(message, statusCode: response.statusCode, code: code);
    }
  }

  /// Start a new Focus episode (supports CT-QF1, CT-LIN1, CT-INEQ1, CT-PAR1, CT-POLY1).
  Future<FocusCommandResult> startEpisode({
    required String episodeId,
    String topicId = 'CT-QF1',
    int? a,
    int b = 5,
    int c = 6,
    String? comparator,
    int? divisorRoot,
    int? x0,
    required String idempotencyKey,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes');
    final Map<String, dynamic> body = {
      'episode_id': episodeId,
      'topic_id': topicId,
      'b': b,
      'c': c,
    };
    if (a != null) body['a'] = a;
    if (comparator != null) body['comparator'] = comparator;
    if (divisorRoot != null) body['divisor_root'] = divisorRoot;
    if (x0 != null) body['x0'] = x0;

    final response = await _client.post(
      uri,
      headers: _buildHeaders(idempotencyKey: idempotencyKey),
      body: jsonEncode(body),
    );

    if (response.statusCode == 201) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Retrieve the current authoritative view of an episode.
  Future<FocusEpisodeView> getEpisode(String episodeId) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId');
    final response = await _client.get(
      uri,
      headers: _buildHeaders(),
    );

    if (response.statusCode == 200) {
      return FocusEpisodeView.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Submit an attempt step with optimistic concurrency control.
  Future<FocusCommandResult> submitAttempt({
    required String episodeId,
    required FocusAttemptInputKind inputKind,
    required dynamic rawInput,
    required String idempotencyKey,
    required int expectedPreviousSequence,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/attempts');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
      body: jsonEncode({
        'input_kind': inputKind.wireName,
        'input': rawInput,
      }),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Submit a diagnostic probe response.
  Future<FocusCommandResult> submitProbeResponse({
    required String episodeId,
    required String probeId,
    required String responseCode,
    required String idempotencyKey,
    required int expectedPreviousSequence,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/probe-responses');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
      body: jsonEncode({
        'probe_id': probeId,
        'response_code': responseCode,
      }),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Request to begin a server-authorized repair intervention.
  Future<FocusCommandResult> beginRepair({
    required String episodeId,
    required String idempotencyKey,
    required int expectedPreviousSequence,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/repair/begin');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Submit learner work on an active intervention.
  Future<FocusCommandResult> submitRepairWork({
    required String episodeId,
    required dynamic rawWork,
    required String idempotencyKey,
    required int expectedPreviousSequence,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/repair/work');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
      body: jsonEncode({
        'raw_work': rawWork,
      }),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Submit original self-correction attempt on the quadratic problem.
  Future<FocusCommandResult> submitOriginalSelfCorrection({
    required String episodeId,
    required FocusAttemptInputKind inputKind,
    required dynamic rawInput,
    required String idempotencyKey,
    required int expectedPreviousSequence,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/repair/self-correction');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
      body: jsonEncode({
        'input_kind': inputKind.wireName,
        'input': rawInput,
      }),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Submit learner attempt on the transfer task.
  Future<FocusCommandResult> submitTransferWork({
    required String episodeId,
    required dynamic rawWork,
    required String idempotencyKey,
    required int expectedPreviousSequence,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/repair/transfer');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
      body: jsonEncode({
        'raw_work': rawWork,
      }),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Schedule a delayed retest for a temporarily recovered KC.
  Future<FocusCommandResult> scheduleRetest({
    required String episodeId,
    required String targetKc,
    required String idempotencyKey,
    required int expectedPreviousSequence,
    String? barrierId,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/retest/schedule');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
      body: jsonEncode({
        'target_kc': targetKc,
        if (barrierId != null) 'barrier_id': barrierId,
      }),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Submit learner work on a delayed retest.
  Future<FocusCommandResult> submitDelayedRetestWork({
    required String episodeId,
    required String targetKc,
    required dynamic rawWork,
    required String idempotencyKey,
    required int expectedPreviousSequence,
    String? barrierId,
  }) async {
    final uri = Uri.parse('$baseUrl/episodes/$episodeId/retest/submit');
    final response = await _client.post(
      uri,
      headers: _buildHeaders(
        idempotencyKey: idempotencyKey,
        expectedSequence: expectedPreviousSequence,
      ),
      body: jsonEncode({
        'target_kc': targetKc,
        'raw_work': rawWork,
        if (barrierId != null) 'barrier_id': barrierId,
      }),
    );

    if (response.statusCode == 200) {
      return FocusCommandResult.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Fetch cross-episode multi-episode learner profile evidence.
  Future<LearnerProfileView> getLearnerProfile() async {
    final uri = Uri.parse('$baseUrl/profile');
    final response = await _client.get(
      uri,
      headers: _buildHeaders(),
    );

    if (response.statusCode == 200) {
      return LearnerProfileView.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Fetch re-entry diagnostic recommendations for a target KC.
  Future<ReEntryDiagnosticView> getReEntryDiagnostic(String targetKc) async {
    final uri = Uri.parse('$baseUrl/diagnostics/re-entry/$targetKc');
    final response = await _client.get(
      uri,
      headers: _buildHeaders(),
    );

    if (response.statusCode == 200) {
      return ReEntryDiagnosticView.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }
    _handleError(response);
  }

  /// Legacy convenience method preserved for backward compatibility.
  Future<FocusEvaluationResponse> evaluateAttempt({
    required String stageId,
    required String rawInput,
    List<int>? expectedConstants,
    List<int>? expectedRoots,
    bool isShortcut = false,
  }) async {
    final uri = Uri.parse('$baseUrl/evaluate-attempt');
    final response = await _client.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'stage_id': stageId,
        'raw_input': rawInput,
        if (expectedConstants != null) 'expected_constants': expectedConstants,
        if (expectedRoots != null) 'expected_roots': expectedRoots,
        'is_shortcut': isShortcut,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return FocusEvaluationResponse.fromJson(data);
    }
    _handleError(response);
  }

  /// Closes the underlying HTTP client to release network sockets.
  void close() {
    _client.close();
  }

  /// Alias for close() to match Flutter's dispose convention.
  void dispose() {
    close();
  }
}
