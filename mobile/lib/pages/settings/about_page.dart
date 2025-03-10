import 'package:flutter/material.dart';
import 'package:shikanet/widgets/widgets.dart';

var explanation =
"""
Whether you're compiling notes from a recent study group or 
recalling important details to prepare for an upcoming meeting, 
this message summarization app is your foremost tool for organizing 
your life.
\t
With this app, you can search through your past conversations 
and receive insightful responses from our chat agent. Have a question 
that you regularly ask? Find it in your recent 
search history. Want to summarize your recent activities across all 
of your linked social media accounts? Our chat agent can help you 
search through your messages on all platforms.
\t
The frontend of the this Material app was built with Flutter, and 
the backend is comprised on a Python Flask server processing 
requests via LLMs.
\t
Thanks to Krishna and Kasten for their hard work on setting up, 
debugging, and evaluating the backend LLMs, and thanks to Richard 
for designing the frontend and user interactions.
""".trim().replaceAll("\n", "").replaceAll("\t", "\n\n");

class AboutPage extends StatelessWidget {
  const AboutPage({super.key});
  
  @override
  Widget build(BuildContext context) {
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
          'About',
          style: TextStyle(color: theme.colorScheme.onSurface, fontWeight: FontWeight.w500))
      ),
      body: Padding(
        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 26),
        child: Column(
          children: [
            SectionHeading(heading: "Sometimes, it's not easy keeping track of all the little details."),
            SizedBox(height: 16),
            Padding(
              padding: EdgeInsets.all(4),
              child: Text(explanation)
            )
          ],
        )
      ),
    );
  }
}