import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flex_color_scheme/flex_color_scheme.dart';
import 'package:shikanet/data/data.dart';
import 'package:shikanet/providers/providers.dart';
import 'package:shikanet/widgets/widgets.dart';
import 'package:shikanet/utils/utils.dart' as util;

class AppearancePage extends ConsumerStatefulWidget {
  const AppearancePage({super.key});

  @override
  ConsumerState<AppearancePage> createState() => _AppearancePageState();
}

class _AppearancePageState extends ConsumerState<AppearancePage> {
  @override
  Widget build(BuildContext context) {
    User user = ref.watch(userInfoProvider);
    ThemeMode currMode = user.appPreferences['appearance'];
    var theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          onPressed: () {
            Navigator.pop(context);
          },
          icon: Icon(Icons.arrow_back, color: theme.colorScheme.onSurface)
        ),
        backgroundColor: theme.colorScheme.surfaceContainerHigh,
        centerTitle: true,
        title: Text(
          'Appearance',
          style: TextStyle(color: theme.colorScheme.onSurface, fontWeight: FontWeight.w500))
      ),
      body: ListView(
        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 26),
        children: [
          SettingsHeading(title: 'Theme'),
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 12),
            child: Text('Controls the base appearance of the app.')
          ),
          SizedBox(height: 20),
          SegmentedButton(
            style: SegmentedButton.styleFrom(
              selectedBackgroundColor: theme.colorScheme.primary,
            ),
            segments: <ButtonSegment<ThemeMode>>[
              ButtonSegment(
                value: ThemeMode.light,
                label: Text(
                  'Light',
                  style: TextStyle(
                    color: currMode == ThemeMode.light ?
                      theme.colorScheme.onPrimary
                      :
                      theme.colorScheme.primary
                  ),
                ),
                icon: Icon(
                  Icons.sunny,
                  color: currMode == ThemeMode.light ?
                    theme.colorScheme.onPrimary
                    :
                    theme.primaryColor
                )
              ),
              ButtonSegment(
                value: ThemeMode.system,
                label: Text(
                  'Auto',
                  style: TextStyle(
                    color: currMode == ThemeMode.system ?
                      theme.colorScheme.onPrimary
                      :
                      theme.colorScheme.primary
                  ),
                ),
                icon: Icon(
                  Icons.smartphone,
                  color: currMode == ThemeMode.system ?
                    theme.colorScheme.onPrimary
                    :
                    theme.primaryColor
                ),
              ),
              ButtonSegment(
                value: ThemeMode.dark,
                label: Text(
                'Dark',
                style: TextStyle(
                    color: currMode == ThemeMode.dark ?
                      theme.colorScheme.onPrimary
                      :
                      theme.colorScheme.primary
                  ),
                ),
                icon: Icon(
                  Icons.nightlight,
                  color: currMode == ThemeMode.dark ?
                    theme.colorScheme.onPrimary
                    :
                    theme.primaryColor
                )
              )
            ],
            selected: <ThemeMode>{currMode},
            showSelectedIcon: false,
            onSelectionChanged: (value) {
              ref.read(userInfoProvider.notifier).update(
                user.copyWith(appPreferences: {'appearance': value.toList().first})
              );
            },
          ),
          SizedBox(height: 20),
          SettingsHeading(title: 'Color'),
          Padding(
            padding: EdgeInsets.symmetric(horizontal: 12),
            child: Text('Sets the color scheme of the app.')
          ),
          SizedBox(height: 10),
          Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: theme.colorScheme.surfaceContainer
            ),
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Align(
                    alignment: Alignment.topLeft,
                    child: Text(user.appPreferences['themeTitle'])
                  ),
                ),
                SingleChildScrollView(
                  padding: EdgeInsets.only(bottom: 30),
                  scrollDirection: Axis.horizontal,
                  physics: ClampingScrollPhysics(),              
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Row(
                      children: [
                        SizedBox(width: 16),
                        ColorGridSample(
                          lightTheme: util.vintageLight,
                          darkTheme: util.vintageDark,
                          themeTitle: 'Vintage',
                        ),
                        for (String s in util.colors.keys)
                          ColorGridSample(
                            lightTheme: FlexThemeData.light(scheme: util.colors[s]),
                            darkTheme: FlexThemeData.dark(scheme: util.colors[s]),
                            themeTitle: s,
                          )
                      ],
                    ),
                  ),
                )
              ],
            )
          ),
        ],
      )
    );
  }
}

