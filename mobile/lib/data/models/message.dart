class Message {
  Message({
    required this.fromUser,
    required this.msg,
    required this.timestamp,
    this.rendered = false
  });

  final bool fromUser;
  final String msg;
  final DateTime timestamp;
  final bool rendered;

  Message copyWith({
    final bool? fromUser,
    final String? msg,
    final DateTime? timestamp,
    final bool? rendered
  }) {
    return Message(
      fromUser: fromUser ?? this.fromUser,
      msg: msg ?? this.msg,
      timestamp: timestamp ?? this.timestamp,
      rendered: rendered ?? this.rendered
    );
  }
}