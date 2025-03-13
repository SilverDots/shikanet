import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';

part 'chat_log_provider.g.dart';

@Riverpod(keepAlive: true)
class ChatLog extends _$ChatLog {
  List<Message> _init() {
    return [Message(
      fromUser: false,
      msg: "Hello, how can I help you?",
      timestamp: DateTime.now()
    )];
  }
  
  @override
  List<Message> build() {
    return _init();
  }

  void addMessage(String msg, bool fromUser, DateTime requestTimestamp) async {
    state = [...state, Message(fromUser: fromUser, msg: msg, timestamp: requestTimestamp)];
    Map<String, dynamic> response = await ref.read(chatResponseProvider(msg).future);
    Message lastMsg = state[state.length - 1];
    if (lastMsg.fromUser && lastMsg.msg == msg && lastMsg.timestamp == requestTimestamp) {
      String answer = response['response'] as String;
      answer = answer.trim();
      if (answer[0] == '"' && answer[answer.length - 1] == '"') {
        answer = answer.substring(1, answer.length - 1);
      }
      answer = answer
        .replaceAll('\\"', '"')
        .replaceAll('\\n', '\n');
      
      List<List<ResponseMessage>> responseSnippets = [];
      var snippets = response['snippets'];
      for (List<dynamic> snippet in snippets) {
        List<ResponseMessage> snippetMessages = [];
        for (Map<String, dynamic> rspMsg in snippet) {
          snippetMessages.add(ResponseMessage.fromJson(rspMsg));
        }
        if (snippetMessages.isEmpty) {
          continue;
        }
        responseSnippets.add(snippetMessages);
      }

      state = [...state, Message(
        fromUser: false,
        msg: answer,
        respQuality: response['grounded'],
        responseSnippets: responseSnippets,
        timestamp: DateTime.now(),
        rendered: lastMsg.rendered
      )];
    }
  }

  Future<void> markRendered(Message m) async {
    Message lastMsg = state[state.length - 1];
    if (lastMsg.fromUser == m.fromUser
        && lastMsg.msg == m.msg
        && lastMsg.timestamp == m.timestamp) {
      List<Message> copy = [...state];
      copy[copy.length - 1] = m.copyWith(rendered: true);
      await Future.delayed(Duration(milliseconds: 200));
      state = copy;
    }
  }

  void reset() {
    state = _init();
  }
}