import 'package:flutter/material.dart';
import 'package:shikanet/widgets/widgets.dart';

class FullWidthButton extends StatelessWidget {
  const FullWidthButton({
    super.key,
    required this.title,
    required this.onTap,
    this.leading,
    this.trailing,
    this.backgroundColor,
    this.textColor,
    this.borderRadius = BorderRadius.zero,
    this.contentPadding = const EdgeInsets.symmetric(horizontal: 20)
  });

  final Function() onTap;
  final String title;
  final Widget? leading;
  final Widget? trailing;
  final Color? backgroundColor;
  final Color? textColor;
  final BorderRadius borderRadius;
  final EdgeInsetsGeometry contentPadding;

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);

    return AnimatedCardButton(
      onTap: onTap,
      borderRadius: borderRadius,
      padding: EdgeInsets.zero,
      backgroundColor: backgroundColor ?? theme.colorScheme.surfaceContainer,
      highlightColor: theme.highlightColor,
      shadow: false,
      child: ListTile(
        leading: leading,
        trailing: trailing,
        title: Text(
          title,
          style: TextStyle(color: textColor ?? theme.colorScheme.onSurface)),
        iconColor: theme.colorScheme.onSurface,
        contentPadding: contentPadding
      ),
    );
  }
}