import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';

class HomePage extends ConsumerWidget {
  const HomePage({super.key});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    User user = ref.watch(userInfoProvider);

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.only(
            top: 12,
            left: 12,
            right: 12
          ),
          child: ListView(
            children: [
              Column(
                children: [
                  TitleCard(
                    title: 'Hello, ${user.firstName}',
                    subtitle: 'Ask questions, view your recent searches, and more.',
                  ),
                  SectionHeading(heading: 'Shortcuts'),
                  HomeShortcutMenu(),
                  SectionHeading(heading: 'Search History'),
                  SearchHistory()
                ],
              )
            ],
          ),
        ),
      )
    );
  }
}