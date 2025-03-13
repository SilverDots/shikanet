import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:shikanet/data/data.dart';

class ChatSource extends StatelessWidget {
  const ChatSource({
    super.key,
    required this.question,
    required this.answer,
    required this.snippets
  });

  final String question;
  final String answer;
  final List<List<ResponseMessage>> snippets;

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.colorScheme.secondaryContainer,
        title: Text(
          "Source",
          style: TextStyle(color: theme.colorScheme.onSecondaryContainer,
          fontWeight: FontWeight.w500)
        ),
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          color: theme.colorScheme.onSecondaryContainer,
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Text('WIP')
    );
  }
}