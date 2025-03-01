import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/pages/pages.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/utils/utils.dart';
import 'package:shikanet/widgets/widgets.dart';

class SearchHistoryCard extends ConsumerWidget {
  const SearchHistoryCard({super.key, required this.data});

  final String data;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    void searchCallback() {
      ref.read(chatLogProvider.notifier)
        .addMessage(data, true, DateTime.now());
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => ChatPage()
        )
      );
      ref.read(questionLogProvider.notifier)
        .addQuestion(data);
    }
    
    return AnimatedCardButton(
      onTap: searchCallback,
      child: ListTile(
        leading: Icon(Icons.message, color: rustorange),
        title: Text(data),
        titleTextStyle: TextStyle(
          color: lightyellow,
          fontSize: 16,
          fontFamily: 'Roboto'
        ),
      )
    );
  }
}