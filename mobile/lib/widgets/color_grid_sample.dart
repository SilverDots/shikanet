import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';

class ColorGridSample extends ConsumerWidget {
  const ColorGridSample({
    super.key,
    required this.lightTheme,
    required this.darkTheme,
    required this.themeTitle
  });

  final ThemeData lightTheme;
  final ThemeData darkTheme;
  final String themeTitle;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    User user = ref.watch(userInfoProvider);
    var currTheme = Theme.of(context);
    var brightness = currTheme.brightness;
    var sampleTheme = brightness == Brightness.light ? lightTheme : darkTheme;
    bool selected = user.appPreferences['lightTheme'] == sampleTheme
      || user.appPreferences['darkTheme'] == sampleTheme;

    return Padding(
      padding: const EdgeInsets.only(
        right: 16
      ),
      child: GestureDetector(
        onTap: () {
          ref.read(userInfoProvider.notifier).update(
            user.copyWith(appPreferences: {
              'lightTheme' : lightTheme,
              'darkTheme' : darkTheme,
              'themeTitle' : themeTitle,
            })
          );
        },
        child: Container(
          height: 50,
          width: 50,
          padding: selected ? EdgeInsets.all(2) : null,
          decoration: selected ?
            BoxDecoration(
              border: Border.all(color: currTheme.colorScheme.outline),
              color: currTheme.colorScheme.surfaceContainerHigh
            )
            :
            null,
          child: GridView.count(
            shrinkWrap: true,
            padding: EdgeInsets.zero,
            physics: NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            children: [
              Container(color: sampleTheme.colorScheme.primary),
              Container(color: sampleTheme.colorScheme.primaryContainer),
              Container(color: sampleTheme.colorScheme.secondary),
              Container(color: sampleTheme.colorScheme.tertiary),
            ],
          ),
        ),
      ),
    );
  }
}