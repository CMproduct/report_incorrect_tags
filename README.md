# Report Incorrect Tags Add-on for Anki

This Anki add-on allows users to quickly report cards with incorrect tags to a centralized Google Form. When reviewing a card that has incorrect tags, simply press the configured hotkey (default: Ctrl+Shift+R) to open a Google Form with pre-filled information about the current card. It was produced by a Mount Sinai student for our curriculum but feel free to use it if it has any value to you.

## Features

- Link any Google Form to quickly report cards with incorrect tags
- Configure your own custom hotkey
- A polished and professional first-run setup popup for a great first impression.
- Works with any shared deck
- Pre-fills the form with card details (deck name, tags, note ID)
- Configuration dialog available in the Tools menu

## Installation

### Method 1: AnkiWeb (Recommended)

1. Open Anki
2. Go to Tools → Add-ons
3. Click "Get Add-ons..."
4. Enter the add-on code: `547965285`
6. Restart Anki
7. Follow the first-run setup instructions

### Method 2: Manual Installation

1. Download the latest release ZIP file
2. Open Anki
3. Go to Tools → Add-ons
4. Click "Install from file..."
5. Select the ZIP file you downloaded
6. Restart Anki
7. Follow the first-run setup instructions

## Setup

When you first run Anki after installing this add-on, a setup wizard will appear:

1. Enter the URL of your Google Form
2. (Optional) Configure the form field IDs
3. Click "OK" to save the configuration

If the setup wizard doesn't appear, you can access it anytime:
1. Go to Tools → Configure Tag Reporter

## Finding Google Form Field IDs (Advanced)

To make the add-on pre-fill your Google Form fields:

1. Create a Google Form with fields for the card information you want to collect
2. Go to your Google Form in a web browser
3. Right-click and select "View Page Source"
4. Search for "entry." in the source code
5. Look for IDs like "entry.123456789" - these are your field IDs
6. In the add-on configuration dialog, enter these IDs for the corresponding fields

## Usage

1. While reviewing cards in Anki, if you encounter a card with incorrect tags
2. Press the configured hotkey (default: Ctrl+Shift+R)
3. Your browser will open with the Google Form pre-filled with information about the current card
4. Complete the form with any additional information and submit

## For Educators and Deck Maintainers

This add-on is perfect for:
- Medical school flashcard collections
- Language learning shared decks
- Community-maintained study materials
- Any educational context where accuracy is important

It allows your students or users to easily report tagging errors, helping you improve your deck quality over time.

## Changelog
## v1.1
- Auto-populated Google Form: Now generates pre-filled links using entry IDs so that card details are automatically filled in.
- Improved Field Mapping Handling: Enhanced mapping between Anki card fields and Google Form entries.
- Minor bug fixes and performance improvements.

## Support

If you encounter any issues or have questions, please:
- Submit an issue on [GitHub](https://github.com/CMproduct/report_incorrect_tags)
- Contact the developer at caleb.massimi@icahn.mssm.edu

## Author

*   **Caleb Massimi**

## License

This project is licensed under the GNU GPL v3 License - see the LICENSE file for details.
