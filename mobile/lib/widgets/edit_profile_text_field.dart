import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:email_validator/email_validator.dart';

class EditProfileTextField extends StatefulWidget {
  const EditProfileTextField({
    super.key,
    required this.name,
    this.initValue,
    this.optional = false,
    required this.controller,
    this.keyboardType = TextInputType.text,
    this.inputFormatters = const [],
    this.prefix = "",
    this.onChange
  });

  final String name;
  final String? initValue;
  final bool optional;
  final TextInputType keyboardType;
  final TextEditingController controller;
  final List<TextInputFormatter> inputFormatters;
  final String prefix;
  final Function(String)? onChange;

  @override
  State<EditProfileTextField> createState() => _EditProfilePageTextFieldState();
}

class _EditProfilePageTextFieldState extends State<EditProfileTextField> {
  String? errorText;

  String? validate(value) {
    widget.onChange;
    if (value.isEmpty && !widget.optional) {
      return "This field cannot be empty.";
    } else if (widget.keyboardType == TextInputType.emailAddress
        && !EmailValidator.validate(value)) {
      return 'Please enter a valid email.';
    }
    return null;
  }
  
  @override
  Widget build(BuildContext context) {
    return TextFormField(
      autocorrect: false,
      maxLength: 64,
      controller: widget.controller,
      keyboardType: widget.keyboardType,
      inputFormatters: widget.inputFormatters,
      onChanged: (value) {
        if (widget.onChange != null) {
          widget.onChange!(value);
        }
        setState(() => errorText = validate(value));
      },
      validator: validate,
      decoration: InputDecoration(
        labelText: widget.name + (widget.optional ? " (optional)" : ""),
        border: OutlineInputBorder(),
        prefix: Text(widget.prefix),
        errorText: errorText,
        floatingLabelBehavior: FloatingLabelBehavior.always,
        counterText: "",
      )
    );
  }
}