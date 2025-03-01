
import 'dart:collection';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'question_log_provider.g.dart';

// Will pull from firebase async later as appropriate
@Riverpod(keepAlive: true)
class QuestionLog extends _$QuestionLog {
  final int maxResults = 6;

  @override
  Queue<String> build() {
    return Queue();
  }

  void addQuestion(String q) {
    final Queue<String> copy = Queue.from(state);
    if (copy.contains(q)) {
      copy.remove(q);
    } else if (state.length == maxResults) {
      copy.removeLast();
    }
    copy.addFirst(q);
    state = copy;
  }
}