import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/utils/utils.dart';
import 'package:shikanet/widgets/widgets.dart';

class ChatPage extends ConsumerWidget {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: rustorange,
        title: Text("Chat", style: TextStyle(color: white, fontWeight: FontWeight.w500))
      ),
      backgroundColor: gold,
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