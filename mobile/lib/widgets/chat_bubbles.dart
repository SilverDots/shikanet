import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/pages/pages.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class ChatBubbles extends ConsumerWidget {
  const ChatBubbles({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    List<Message> chatLog = ref.watch(chatLogProvider);
    var theme = Theme.of(context);

    Widget generateBubble(Message msg, String? query, BorderRadius br, Color bgColor, Color textColor) {
      return Flexible(
        flex: 3,
        child: msg.fromUser ?
          Container(
            decoration: BoxDecoration(
              color: bgColor,
              borderRadius: br
            ),
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text(msg.msg, style: TextStyle(color: textColor))
            )
          )
          :
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                decoration: BoxDecoration(
                  color: bgColor,
                  borderRadius: br
                ),
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: MarkdownBody(
                    data: msg.msg,
                    shrinkWrap: true,
                    styleSheet: MarkdownStyleSheet(
                      p: TextStyle(color: textColor),
                      listBullet: TextStyle(color: theme.colorScheme.onSurface),
                      code: TextStyle(color: theme.colorScheme.onSurface)
                    ),
                  )
                )
              ),
              if (query != null && msg.responseSnippets != null)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8.0),
                  child: HighlightableText(
                    text: 'Details',
                    onTap: () {
                      Navigator.of(context).push(MaterialPageRoute(
                        builder:(context) => ChatSource(
                          question: query,
                          answer: msg.msg,
                          quality: msg.respQuality!,
                          snippets: msg.responseSnippets!
                        ),
                      ));
                    }
                  ),
                )
            ],
          )
      );
    }

    List<Widget> generateChatBubbles(List<Message> log) {
      List<Widget> bubbles = [];
      Radius radius = const Radius.circular(16);
      BorderRadius userMessageBorder = BorderRadius.only(bottomLeft: radius, topLeft: radius, topRight: radius);
      BorderRadius appMessageBorder = BorderRadius.only(bottomLeft: radius, bottomRight: radius, topRight: radius);
      
      // Process the log messages in reverse because the ListView
      // in the build() method will reverse them again.
      // List<Message> reversedLog = log.reversed.toList();
      for (int idx = log.length - 1; idx >= 0; idx--) {
        Message m = log[idx];
        Widget child1 = m.fromUser ? Spacer() : generateBubble(
          m,
          idx != 0 ? log[idx - 1].msg : null,
          appMessageBorder,
          theme.colorScheme.surfaceContainerHighest,
          theme.colorScheme.onSurface);
        Widget child2 = m.fromUser ? generateBubble(
          m,
          null,
          userMessageBorder,
          theme.colorScheme.primary,
          theme.colorScheme.onPrimary) : Spacer();

        bubbles.add(Padding(
          padding: const EdgeInsets.only(top: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [child1, child2]
          ),
        ));
      }

      // Check if last message in the original log was sent by the user
      if (log.last.fromUser && !log.last.rendered) {
        // Animate the last (user) message
        bubbles[0] = AnimatedBubble(
          duration: const Duration(milliseconds: 800),
          alignment: Alignment.bottomRight,
          message: log.last,
          child: bubbles[0], 
        );

        // Add a typing indicator for the chat agent. The indicator
        // should be inserted as the first element of the returned
        // list so that it appears at the bottom when the list is reversed.
        bubbles.insert(0, AnimatedBubble(
          duration: Duration(milliseconds: 1000),
          alignment: Alignment.bottomLeft,
          child: Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Flexible(
                  flex: 3,
                  child: Container(
                    decoration: BoxDecoration(
                      color: theme.colorScheme.surfaceContainerHighest,
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
          ),
        ));
      } else if (log.last.fromUser) {
        bubbles.insert(0, Padding(
          padding: const EdgeInsets.only(top: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                flex: 3,
                child: Container(
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
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
      } else if (!log.last.fromUser && !log.last.rendered) {
        // If the last message is from the app but is not marked as rendered,
        // then add a bubble animation.
        bubbles[0] = AnimatedBubble(
          duration: const Duration(milliseconds: 1000),
          alignment: Alignment.bottomLeft,
          message: log.last,
          child: bubbles[0]
        );

        // Further, if the message prior to the app message has yet to be rendered,
        // animate that message, too.
        if (log.length > 1 && !log[log.length - 2].rendered) {
          bubbles[1] = AnimatedBubble(
            duration: const Duration(milliseconds: 800),
            alignment: Alignment.bottomRight,
            message: log.last,
            child: bubbles[1],
          );
        }
      }
      return bubbles;
    }

    var bubbles = generateChatBubbles(chatLog);

    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: Align(
          alignment: Alignment.topCenter,
          child: ListView.builder(
            reverse: true,
            shrinkWrap: true,
            itemBuilder: (context, index) {
              return bubbles[index];
            },
            itemCount: bubbles.length,
          )
        ),
      )
    );
  }
}