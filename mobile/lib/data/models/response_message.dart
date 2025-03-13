class ResponseMessage {
  const ResponseMessage({
    required this.sender,
    required this.datetime,
    required this.msg,
    required this.platform,
    required this.chat
  });

  final String sender;
  final String datetime;
  final String msg;
  final String platform;
  final String chat;

  ResponseMessage.fromJson(Map<String, dynamic> json)
    : sender = json['SENDER'] as String,
      datetime = json['DATETIME'] as String,
      msg = json['MESSAGE'] as String,
      platform = json['PLATFORM'] as String,
      chat = json['CHAT'] as String;
}