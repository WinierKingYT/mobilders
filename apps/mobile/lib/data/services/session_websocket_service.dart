import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../core/constants.dart';

class SessionWebSocketService {
  final String serverUrl;
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;

  bool _isConnected = false;
  bool get isConnected => _isConnected;

  bool _isDisposed = false;
  bool get isDisposed => _isDisposed;

  static const int maxQueuedEvents = 100;
  final List<Map<String, dynamic>> _offlineQueue = [];
  int get queuedEventsCount => _offlineQueue.length;

  final StreamController<Map<String, dynamic>> _messageController =
      StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;

  final StreamController<Map<String, dynamic>> _affectiveAlertController =
      StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get affectiveAlerts => _affectiveAlertController.stream;

  SessionWebSocketService({
    String? url,
  }) : serverUrl = url ?? "${ApiConstants.baseUrl.replaceFirst('http', 'ws')}/ws/v1/session";

  void connect() {
    if (_isDisposed) return;
    if (_isConnected || _channel != null) {
      disconnect();
    }
    try {
      final uri = Uri.parse(serverUrl);
      _channel = WebSocketChannel.connect(uri);

      _subscription = _channel?.stream.listen(
        (message) {
          if (_isDisposed) return;
          try {
            final Map<String, dynamic> data = jsonDecode(message as String);
            if (data["type"] == "SESSION_READY") {
              _isConnected = true;
              _flushOfflineQueue();
            } else if (data["type"] == "AFFECTIVE_ALERT") {
              final payload = data["payload"];
              if (payload is Map<String, dynamic> && !_affectiveAlertController.isClosed) {
                _affectiveAlertController.add(payload);
              }
            }
            if (!_messageController.isClosed) {
              _messageController.add(data);
            }
          } catch (e) {
            debugPrint("WS parse error: $e");
          }
        },
        onError: (error) {
          debugPrint("WS error: $error");
          _isConnected = false;
          _subscription?.cancel();
          _subscription = null;
          _channel = null;
        },
        onDone: () {
          debugPrint("WS connection closed");
          _isConnected = false;
          _subscription?.cancel();
          _subscription = null;
          _channel = null;
        },
      );
    } catch (e) {
      debugPrint("WS connection initiation error: $e");
      _isConnected = false;
    }
  }

  void _flushOfflineQueue() {
    if (!_isConnected || _channel == null || _isDisposed) return;
    while (_offlineQueue.isNotEmpty) {
      final event = _offlineQueue.removeAt(0);
      try {
        _channel!.sink.add(jsonEncode(event));
      } catch (e) {
        // Put back and abort flush
        _offlineQueue.insert(0, event);
        break;
      }
    }
  }

  void sendEvent(Map<String, dynamic> event) {
    if (_isDisposed) return;
    if (_isConnected && _channel != null) {
      try {
        _channel!.sink.add(jsonEncode(event));
      } catch (e) {
        _isConnected = false;
        _enqueueOfflineEvent(event);
      }
    } else {
      _enqueueOfflineEvent(event);
    }
  }

  void _enqueueOfflineEvent(Map<String, dynamic> event) {
    if (_offlineQueue.length >= maxQueuedEvents) {
      _offlineQueue.removeAt(0);
    }
    _offlineQueue.add(event);
  }

  void sendStepSubmit({
    required String rawLatex,
    required String previousStep,
    required double latencyMs,
    int hesitationPausesCount = 0,
    String targetEquation = "x**2 + 6*x - 2 = 0",
  }) {
    sendEvent({
      "type": "STEP_SUBMIT",
      "client_msg_id": "cmsg_${DateTime.now().millisecondsSinceEpoch}",
      "payload": {
        "raw_latex": rawLatex,
        "previous_canonical": previousStep,
        "target_equation": targetEquation,
        "input_mode": "touchpad",
        "latency_ms": latencyMs,
        "hesitation_pauses_count": hesitationPausesCount,
        "client_timestamp": DateTime.now().toIso8601String(),
      }
    });
  }

  void sendConfidenceSubmit(double confidenceLevel) {
    sendEvent({
      "type": "CONFIDENCE_SUBMIT",
      "client_msg_id": "cmsg_conf_${DateTime.now().millisecondsSinceEpoch}",
      "payload": {
        "confidence_level": confidenceLevel,
        "client_timestamp": DateTime.now().toIso8601String(),
      }
    });
  }

  void sendHintRequest(
    String currentLatex, {
    String targetEquation = "x**2 + 6*x - 2 = 0",
  }) {
    sendEvent({
      "type": "HINT_REQUEST",
      "client_msg_id": "cmsg_hint_${DateTime.now().millisecondsSinceEpoch}",
      "payload": {
        "current_latex": currentLatex,
        "target_equation": targetEquation,
      }
    });
  }

  void disconnect() {
    _subscription?.cancel();
    _subscription = null;
    try {
      _channel?.sink.close();
    } catch (_) {}
    _channel = null;
    _isConnected = false;
  }

  void dispose() {
    _isDisposed = true;
    disconnect();
    if (!_messageController.isClosed) {
      _messageController.close();
    }
    if (!_affectiveAlertController.isClosed) {
      _affectiveAlertController.close();
    }
  }
}
