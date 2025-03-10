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
    String response = await ref.read(chatResponseProvider(msg).future);
    Message lastMsg = state[state.length - 1];
    if (lastMsg.fromUser && lastMsg.msg == msg && lastMsg.timestamp == requestTimestamp) {
      state = [...state, Message(
        fromUser: false,
        msg: response,
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