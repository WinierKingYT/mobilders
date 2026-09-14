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

  final List<Map<String, dynamic>> _offlineQueue = [];
  int get queuedEventsCount => _offlineQueue.length;

  final StreamController<Map<String, dynamic>> _messageController =
      StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;

  SessionWebSocketService({
    String? url,
  }) : serverUrl = url ?? "${ApiConstants.baseUrl.replaceFirst('http', 'ws')}/ws/v1/session";

  void connect() {
    try {
      final uri = Uri.parse(serverUrl);
      _channel = WebSocketChannel.connect(uri);

      _subscription = _channel?.stream.listen(
        (message) {
          try {
            final Map<String, dynamic> data = jsonDecode(message as String);
            if (data["type"] == "SESSION_READY") {
              _isConnected = true;
              _flushOfflineQueue();
            }
            _messageController.add(data);
          } catch (e) {
            debugPrint("WS parse error: $e");
          }
        },
        onError: (error) {
          debugPrint("WS error: $error");
          _isConnected = false;
        },
        onDone: () {
          debugPrint("WS connection closed");
          _isConnected = false;
        },
      );
    } catch (e) {
      debugPrint("WS connection initiation error: $e");
      _isConnected = false;
    }
  }

  void _flushOfflineQueue() {
    if (!_isConnected || _channel == null) return;
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
    if (_isConnected && _channel != null) {
      try {
        _channel!.sink.add(jsonEncode(event));
      } catch (e) {
        _isConnected = false;
        _offlineQueue.add(event);
      }
    } else {
      // Buffer in offline queue
      _offlineQueue.add(event);
    }
  }

  void sendStepSubmit({
    required String rawLatex,
    required String previousStep,
    required double latencyMs,
    int hesitationPausesCount = 0,
  }) {
    sendEvent({
      "type": "STEP_SUBMIT",
      "client_msg_id": "cmsg_${DateTime.now().millisecondsSinceEpoch}",
      "payload": {
        "raw_latex": rawLatex,
        "previous_canonical": previousStep,
        "target_equation": "x**2 + 6*x - 2 = 0",
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

  void sendHintRequest(String currentLatex) {
    sendEvent({
      "type": "HINT_REQUEST",
      "client_msg_id": "cmsg_hint_${DateTime.now().millisecondsSinceEpoch}",
      "payload": {
        "current_latex": currentLatex,
      }
    });
  }

  void disconnect() {
    _subscription?.cancel();
    _channel?.sink.close();
    _isConnected = false;
  }

  void dispose() {
    disconnect();
    _messageController.close();
  }
}
