import 'package:flutter/material.dart';
import 'package:shikanet/utils/utils.dart';
import 'package:shikanet/widgets/widgets.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: gold,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: ListView(
            children: [
              Column(
                children: [
                  HomeTitleCard(),
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