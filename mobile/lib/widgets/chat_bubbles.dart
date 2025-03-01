import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/utils/utils.dart';
import 'package:shikanet/widgets/widgets.dart';

class ChatBubbles extends ConsumerWidget {
  const ChatBubbles({super.key});

  Widget _generateBubble(Message msg, BorderRadius br, Color bgColor, Color textColor) {
    return Flexible(
      flex: 3,
      child: Container(
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: br
        ),
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: msg.fromUser ? 
            Text(msg.msg, style: TextStyle(color: textColor))
            :
            MarkdownBody(
              data: msg.msg,
              shrinkWrap: true,
              styleSheet: MarkdownStyleSheet(
                p: TextStyle(color: textColor),
                listBullet: TextStyle(color: white),
                code: TextStyle(color: white)
              ),
            )
        )
      )
    );
  }

  List<Widget> _generateChatBubbles(List<Message> log) {
    List<Widget> bubbles = [];
    Radius radius = const Radius.circular(16);
    BorderRadius userMessageBorder = BorderRadius.only(bottomLeft: radius, topLeft: radius, topRight: radius);
    BorderRadius appMessageBorder = BorderRadius.only(bottomLeft: radius, bottomRight: radius, topRight: radius);
    
    // Process the log messages in reverse because the ListView
    // in the build() method will reverse them again.
    for (Message m in log.reversed.toList()) {
      Widget child1 = m.fromUser ? Spacer() : _generateBubble(m, appMessageBorder, black, white);
      Widget child2 = m.fromUser ? _generateBubble(m, userMessageBorder, lightyellow, black) : Spacer();

      bubbles.add(Padding(
        padding: const EdgeInsets.only(top: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [child1, child2]
        ),
      ));
    }

    // If the last message in the original log was sent by the user,
    // add a typing indicator for the chat agent. The indicator
    // should be inserted as the first element of the returned
    // list so that it appears at the bottom when the list is reversed.
    if (log.last.fromUser) {
      bubbles.insert(0, Padding(
        padding: const EdgeInsets.only(top: 16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Flexible(
              flex: 3,
              child: Container(
                decoration: BoxDecoration(
                  color: black,
                  borderRadius: appMessageBorder
                ),
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: TypingIndicator()
                )
              ),
            ),
            Spacer()
          ]
        ),
      ));
    }
    return bubbles;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    List<Message> chatLog = ref.watch(chatLogProvider);

    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Align(
          alignment: Alignment.topCenter,
          child: ListView(
            reverse: true,
            shrinkWrap: true,
            children: _generateChatBubbles(chatLog)
          )
        ),
      )
    );
  }
}