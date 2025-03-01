import 'package:flutter/material.dart';
import 'package:shikanet/utils/utils.dart';

class HomeTitleCard extends StatelessWidget {
  const HomeTitleCard({super. key, this.user = 'Kasten'});

  final String user;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: rustorange,
      child: Row(
        children: [
          Flexible(
            flex: 4,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 30),
              child: ListTile(
                title: Text('Hello, $user'),
                subtitle: Text("Ask questions, view your recent searches, and more."),
                titleTextStyle: TextStyle(
                  fontFamily: 'Roboto',
                  fontWeight: FontWeight.bold,
                  fontSize: 30,
                  color: white,
                ),
                subtitleTextStyle: TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: black,
                  height: 1.75
                ),
              ),
            ),
          ),
          Spacer()
        ],
      ),
    );
  }
}