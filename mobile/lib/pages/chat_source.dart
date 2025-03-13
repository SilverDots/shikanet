import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:shikanet/data/data.dart';

class ChatSource extends StatelessWidget {
  const ChatSource({
    super.key,
    required this.question,
    required this.answer,
    required this.snippets,
    required this.quality
  });

  final String question;
  final String answer;
  final List<List<ResponseMessage>> snippets;
  final String quality;

  Widget renderSnippets(ThemeData theme) {
    TextStyle boldStyle = TextStyle(
      fontWeight: FontWeight.bold,
      color: theme.colorScheme.onSurface
    );
    TextStyle italicsStyle = TextStyle(
      fontWeight: FontWeight.normal,
      fontStyle: FontStyle.italic,
      color: theme.colorScheme.onSurface
    );
    
    List<Widget> children = [];
    for (int i = 0; i < snippets.length; i++) {
      List<ResponseMessage> snippet = snippets[i];
      String platform = snippet[0].platform;
      String chat = snippet[0].chat.substring(5);
      children.add(Padding(
        padding: const EdgeInsets.symmetric(vertical: 16.0),
        child: Row(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  color: theme.colorScheme.surfaceContainerHighest,
                ),
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Snippet ${i + 1}',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 20,
                          color: theme.colorScheme.onSurface
                        )
                      ),
                      RichText(
                        text: TextSpan(
                          style: boldStyle,
                          text: 'Platform: ',
                          children: [
                            TextSpan(
                              text: platform,
                              style: italicsStyle
                            )
                          ]
                        ),
                      ),
                      RichText(
                        text: TextSpan(
                          style: boldStyle,
                          text: 'Chat Name: ',
                          children: [
                            TextSpan(
                              text: chat,
                              style: italicsStyle
                            )
                          ]
                        ),
                      ),
                      for (ResponseMessage rm in snippet)
                        Padding(
                          padding: const EdgeInsets.only(top: 8.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              RichText(
                                text: TextSpan(
                                  text: '${rm.sender} ',
                                  style: italicsStyle,
                                  children: [
                                    TextSpan(
                                      style: TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.normal,
                                        fontStyle: FontStyle.normal,
                                        color: theme.colorScheme.onSurface
                                      ),
                                      text: 'on ${rm.datetime}'
                                    )
                                  ]
                                )
                              ),
                              MarkdownBody(
                                data: rm.msg,
                                styleSheet: MarkdownStyleSheet(
                                  p: TextStyle(color: theme.colorScheme.onSurface),
                                  listBullet: TextStyle(color: theme.colorScheme.onSurface),
                                  code: TextStyle(color: theme.colorScheme.onSurface)
                                ),
                              )
                            ],
                          ),
                        )
                    ],
                  ),
                )
              ),
            )
          ],
        ),
      ));
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: children);
  }

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);
    TextStyle boldStyle = TextStyle(
      fontWeight: FontWeight.bold,
      color: theme.colorScheme.onSurface
    );
    TextStyle normalStyle = TextStyle(
      color: theme.colorScheme.onSurface
    );
    String qualityText;
    Color qualityTextColor;
    if (quality == 'yes') {
      qualityText = 'decently grounded in truth';
      qualityTextColor = Colors.blue;
    } else if (quality == 'no') {
      qualityText = 'may not be grounded in truth';
      qualityTextColor = Colors.yellow;
    } else {
      qualityText = 'may poorly reflect past message histories.';
      qualityTextColor = Colors.red;
    }

    Widget body;
    if (snippets.isEmpty) {
      body = Text(
        'No conversation snippets available.',
        style: TextStyle(color: theme.colorScheme.onPrimary)
      );
    } else {
      body = renderSnippets(theme);
    }

    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.colorScheme.secondaryContainer,
        title: Text(
          "Details",
          style: TextStyle(color: theme.colorScheme.onSecondaryContainer,
          fontWeight: FontWeight.w500)
        ),
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          color: theme.colorScheme.onSecondaryContainer,
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 20.0),
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      color: theme.colorScheme.surfaceContainerHighest,
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Question:', style: boldStyle),
                          Text(question, style: normalStyle),
                          SizedBox(height: 8),
                          RichText(
                            text: TextSpan(
                              style: boldStyle,
                              text: 'Our critic determined that the following response is ',
                              children: [
                                TextSpan(
                                  text: qualityText,
                                  style: TextStyle(fontWeight: FontWeight.bold, color: qualityTextColor)
                                ),
                                TextSpan(text: '.', style: boldStyle)
                              ]
                            ),
                          ),
                          SizedBox(height: 8),
                          Text('Answer:', style: boldStyle),
                          Text(answer, style: normalStyle),
                          SizedBox(height: 8),
                        ],
                      ),
                    )
                  ),
                ),
              ],
            ),
          ),
          body,
          SizedBox(height: 30)
        ],
      )
    );
  }
}