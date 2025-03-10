import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/pages/pages.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class HomeShortcutMenu extends ConsumerWidget {
  const HomeShortcutMenu({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    var theme = Theme.of(context);

    void newSearchCallback() {
      ref.read(chatLogProvider.notifier)
        .reset();
      ref.read(chatFieldTextProvider)
        .clear();
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => ChatPage()
        )
      );
    }

    void summarizeCallback() {
      ref.read(chatLogProvider.notifier)
        .addMessage("Summarize my recent activity.", true, DateTime.now());
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (context) => ChatPage()
        )
      );
      User user = ref.read(userInfoProvider);
      if (!user.appPreferences["pauseHistory"]) {
        ref.read(questionLogProvider.notifier)
          .addQuestion("Summarize my recent activity.");
      }
    }

    return IntrinsicHeight(
      child: Row(
        children: [
          Expanded(
            child: ShortcutButton(
              text: 'Start a new search',
              icon: Icon(
                FontAwesomeIcons.magnifyingGlass,
                size: 30,
                color: theme.colorScheme.secondary
              ),
              onTap: newSearchCallback
            )
          ),
          Expanded(
            child: ShortcutButton(
              text: 'Summarize my recent activity',
              icon: Icon(
                FontAwesomeIcons.lightbulb,
                size: 30,
                color: theme.colorScheme.secondary
              ),
              onTap: summarizeCallback
            )
          ),
        ],
      ),
    );
  }
}