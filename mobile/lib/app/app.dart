import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_libphonenumber/flutter_libphonenumber.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'home_view.dart';

class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    User user = ref.watch(userInfoProvider);
    
    return FutureBuilder(
      future: init(),
      builder: (context, snapshot) {
        // No error handling, should be fine to assume this
        // works
        return _EagerInitialization(
          child: MaterialApp(
            theme: user.appPreferences['lightTheme'],
            darkTheme: user.appPreferences['darkTheme'],
            themeMode: user.appPreferences['appearance'],
            home: HomeView()
          ),
        );
      }
    );
  }
}

class _EagerInitialization extends ConsumerWidget {
  const _EagerInitialization({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.watch(phoneFormatterProvider);
    return child;
  } 
}