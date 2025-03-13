import 'package:shikanet/data/data.dart';

class Message {
  Message({
    required this.fromUser,
    required this.msg,
    this.respQuality,
    this.responseSnippets,
    required this.timestamp,
    this.rendered = false
  });

  final bool fromUser;
  final String msg;
  final String? respQuality;
  final List<List<ResponseMessage>>? responseSnippets;
  final DateTime timestamp;
  final bool rendered;

  Message copyWith({
    final bool? fromUser,
    final String? msg,
    final DateTime? timestamp,
    final bool? rendered,
    final List<List<ResponseMessage>>? responseSnippets,
    final String? respQuality
  }) {
    return Message(
      fromUser: fromUser ?? this.fromUser,
      msg: msg ?? this.msg,
      timestamp: timestamp ?? this.timestamp,
      rendered: rendered ?? this.rendered,
      responseSnippets: responseSnippets ?? this.responseSnippets,
      respQuality: respQuality ?? this.respQuality
    );
  }
}