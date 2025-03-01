import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/pages/pages.dart';

class HomeView extends ConsumerStatefulWidget {
  const HomeView({super.key});

  @override
  HomeViewState createState() => HomeViewState();
}

class HomeViewState extends ConsumerState<HomeView> {
  int selectedIndex = 0;
  TextEditingController chatController = TextEditingController();
  
  @override
  Widget build(BuildContext context) {
    Widget page = Container();
    if (selectedIndex == 0) {
      page = HomePage();
    } else if (selectedIndex == 1) {
      page = ChatPage();
    } else {
      page = SettingsPage();
    }
    
    return Scaffold(
      body: Column(
        children: [
          Expanded(
            child: page,
          ),
          NavigationBar(
            selectedIndex: selectedIndex,
            onDestinationSelected: (value) {
              // If navigating to the Chat page, push the route
              // instead of changing the active page.
              if (value == 1) {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => ChatPage()
                  )
                );
              } else {
                setState(() {
                  selectedIndex = value;
                });
              }
            },
            destinations: [
              NavigationDestination(
                icon: Icon(Icons.home_outlined, ),
                selectedIcon: Icon(Icons.home),
                label: 'Home'
              ),
              NavigationDestination(
                icon: Icon(Icons.chat_outlined),
                label: 'Chat'
              ),
              NavigationDestination(
                icon: Icon(Icons.person_outlined),
                selectedIcon: Icon(Icons.person),
                label: "Profile"
              )
            ] 
          )
        ],
      )
    );
  }
}