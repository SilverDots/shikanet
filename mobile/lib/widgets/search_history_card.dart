import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/pages/pages.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class SearchHistoryCard extends ConsumerWidget {
  const SearchHistoryCard({super.key, required this.data});

  final String data;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    var theme = Theme.of(context);
    
    void searchCallback() {
      ref.read(chatLogProvider.notifier)
        .addMessage(data, true, DateTime.now());
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => ChatPage()
        )
      );
      User user = ref.read(userInfoProvider);
      if (!user.appPreferences['pauseHistory']) {
        ref.read(questionLogProvider.notifier)
          .addQuestion(data);
      }
    }

    return AnimatedCardButton(
      onTap: searchCallback,
      child: ListTile(
        leading: Icon(Icons.message, color: theme.colorScheme.secondary),
        title: Text(data),
        titleTextStyle: TextStyle(
          color: theme.colorScheme.onSecondaryContainer,
          fontSize: 16,
          fontFamily: 'Roboto'
        ),
      )
    );
  }
}