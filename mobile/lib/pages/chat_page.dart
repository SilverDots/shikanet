import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/widgets/widgets.dart';

class ChatPage extends ConsumerWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    var theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        backgroundColor: theme.colorScheme.secondaryContainer,
        title: Text(
          "Chat",
          style: TextStyle(color: theme.colorScheme.onSecondaryContainer,
          fontWeight: FontWeight.w500)
        ),
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          color: theme.colorScheme.onSecondaryContainer,
          onPressed: () => Navigator.pop(context),
        ),
      ),
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: Column(
          children: [
            ChatBubbles(),
            SizedBox(height: 16),
            ChatInputBar(),
            SizedBox(height: 16),
          ],
        ),
      )
    );
  }
}