import 'package:flutter/material.dart';
import 'package:flex_color_scheme/flex_color_scheme.dart';

var defaultPreferences = {
  'pauseHistory' : false,
  'appearance' : ThemeMode.system,
  'lightTheme' : FlexThemeData.light(scheme: FlexScheme.brandBlue),
  'darkTheme' : FlexThemeData.dark(scheme: FlexScheme.brandBlue),
  'themeTitle' : 'Brand blue'
};