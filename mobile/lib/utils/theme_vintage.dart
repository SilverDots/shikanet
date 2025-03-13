import 'package:flex_color_scheme/flex_color_scheme.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart'; 

ThemeData vintageLight = FlexThemeData.light(
  colors: const FlexSchemeColor( // Custom colors
    primary: Color(0xFFB23A48),
    primaryContainer: Color(0xFFF4F4F9),
    primaryLightRef: Color(0xFFB23A48),
    secondary: Color(0xFFF4E3B2),
    secondaryContainer: Color(0xFF2B2B2A),
    secondaryLightRef: Color(0xFFF4E3B2),
    tertiary: Color(0xFF5B1D24),
    tertiaryContainer: Color(0xFFF4F4F9),
    tertiaryLightRef: Color(0xFF5B1D24),
    appBarColor: Color(0xFF2B2B2A),
    error: Color(0xFFBA1A1A),
    errorContainer: Color(0xFFFFDAD6),
  ),
  subThemesData: const FlexSubThemesData(
    interactionEffects: true,
    tintedDisabledControls: true,
    useM2StyleDividerInM3: true,
    inputDecoratorIsFilled: true,
    inputDecoratorBorderType: FlexInputBorderType.outline,
    alignedDropdown: true,
    navigationRailUseIndicator: true,
    navigationRailLabelType: NavigationRailLabelType.all,
  ),
  visualDensity: FlexColorScheme.comfortablePlatformDensity,
  cupertinoOverrideTheme: const CupertinoThemeData(applyThemeToAll: true),
);

ThemeData vintageDark = FlexThemeData.dark(
  colors: const FlexSchemeColor( // Custom colors
    primary: Color(0xFFEFC88B),
    primaryContainer: Color(0xFF2B2B2A),
    primaryLightRef: Color(0xFFB23A48),
    secondary: Color(0xFFF4F4F9),
    secondaryContainer: Color(0xFFB23A48),
    secondaryLightRef: Color(0xFFF4E3B2),
    tertiary: Color(0xFF5B1D24),
    tertiaryContainer: Color(0xFFF4F4F9),
    tertiaryLightRef: Color(0xFF5B1D24),
    appBarColor: Color(0xFF2B2B2A),
    error: Color(0xFFFFB4AB),
    errorContainer: Color(0xFF93000A),
  ),
  subThemesData: const FlexSubThemesData(
    interactionEffects: true,
    tintedDisabledControls: true,
    blendOnColors: true,
    useM2StyleDividerInM3: true,
    inputDecoratorIsFilled: true,
    inputDecoratorBorderType: FlexInputBorderType.outline,
    alignedDropdown: true,
    navigationRailUseIndicator: true,
    navigationRailLabelType: NavigationRailLabelType.all,
  ),
  visualDensity: FlexColorScheme.comfortablePlatformDensity,
  cupertinoOverrideTheme: const CupertinoThemeData(applyThemeToAll: true),
);