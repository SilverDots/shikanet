class ResponseMessage {
  const ResponseMessage({
    required this.user,
    required this.timestamp,
    required this.msg
  });

  final String user;
  final String timestamp;
  final String msg;

  ResponseMessage.fromJson(Map<String, dynamic> json)
    : user = json['user'] as String,
      timestamp = json['timestamp'] as String,
      msg = json['msg'] as String;
}