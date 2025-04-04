# Report Incorrect Tags Add-on for Anki
# Version: 1.1
# License: GNU GPL v3

from aqt import mw
from aqt.qt import *
from aqt.utils import openLink, showInfo, getText, askUser
from anki.hooks import addHook
import urllib.parse
import os
import json

# Get the add-on directory
addon_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(addon_dir, "config.json")

# Default mappings for Mount Sinai institution
# These will be used IF the user hasn't configured their own mappings
DEFAULT_FIELD_MAPPINGS = {
    "entry.236929392": "deck_name",
    "entry.1752016781": "tags",
    "entry.427394651": "ankihub_id",    # Changed to ankihub_id based on your list/order
    "entry.596906588": "Text",      # MUST match Anki field name exactly
    "entry.1421260374": "Extra",       # MUST match Anki field name exactly
    # The "Reporter Comments" field (entry.1530349988) is for the user to fill in.
    # The 8th field (entry.1921388369) is not mapped by default.
}

# Default configuration
DEFAULT_CONFIG = {
    "google_form_url": "",
    "hotkey": "Ctrl+Shift+R",
    "form_fields": {
        "deck_name": "",
        "tags": "",
        "note_id": ""
    },
    "use_default_mappings": True,  # New option to use the Mount Sinai default mappings
    "first_run": True
}

def load_config():
    """Load configuration from config.json or create with defaults if not exists."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to config.json."""
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

config = load_config()

def first_run_setup():
    """Show first-run setup dialog and collect necessary information."""
    if not config.get("first_run", True):
        return
    
    # Welcome message
    showInfo("""
    <h1>Thank you for installing the Report Incorrect Tags Add-on! (a CMproduction)</h1>
    <p>This add-on allows you to quickly report cards with incorrect tags to a Google Form.</p>
    <p>Let's set up your Google Form URL and field mappings.</p>
    """)
    
    # Ask if user is from Mount Sinai
    is_mount_sinai = askUser("Are you from Mount Sinai institution?")
    config["use_default_mappings"] = is_mount_sinai
    
    # Get Google Form URL
    form_url, ok = getText("Enter your Google Form URL:", title="Setup Incorrect Tags Reporter")
    if ok and form_url:
        config["google_form_url"] = form_url
    else:
        # If canceled, we'll leave the field blank and ask again next time
        return
    
    # Get Form Field IDs (optional) - only if not using default Mount Sinai mappings
    if not config["use_default_mappings"]:
        show_advanced = askUser("Would you like to configure the form field IDs? (Advanced)")
        if show_advanced:
            for field, default in config["form_fields"].items():
                field_id, ok = getText(
                    f"Enter the Google Form field ID for {field}:\n(Format: entry.123456789)", 
                    title="Form Field Setup",
                    default=default
                )
                if ok:
                    config["form_fields"][field] = field_id
    
    # Set first_run to False
    config["first_run"] = False
    
    # Save configuration
    save_config(config)
    
    showInfo("""
    <h1>Setup Complete!</h1>
    <p>You can now report cards with incorrect tags by pressing {}</p>
    <p>On macOS, use Command+Shift+R instead of Ctrl+Shift+R.</p>
    <p>You can change these settings anytime through Tools → Add-ons → Report Incorrect Tags → Config</p>
    """.format(config["hotkey"]))

def get_current_card_info():
    """Get information about the currently reviewed card."""
    if not mw.reviewer.card:
        return None
    
    card = mw.reviewer.card
    note = card.note()
    
    # Collect relevant information
    card_info = {
        "deck_name": mw.col.decks.name(card.did),
        "note_id": note.id,
        "ankihub_id": note.id,  # Adding ankihub_id as per the default mappings
        "card_id": card.id,
        "tags": " ".join(note.tags),
        "fields": {}
    }
    
    # Add all fields from the note
    for name, value in note.items():
        card_info["fields"][name] = value
        # Also add fields directly to the top level for easier access in form submissions
        card_info[name] = value
    
    return card_info

def report_incorrect_tag():
    """Report the current card as having incorrect tags."""
    # Check if the Google Form URL is set
    if not config["google_form_url"]:
        result = askUser("No Google Form URL is configured. Would you like to configure it now?")
        if result:
            config["first_run"] = True
            first_run_setup()
            return
        else:
            return
    
    # Get current card information
    card_info = get_current_card_info()
    
    if not card_info:
        showInfo("No card is currently being reviewed. Please open a card first.")
        return
    
    # Prepare data for the Google Form
    params = {}
    
    # Use default mappings if enabled, otherwise use custom form fields
    if config.get("use_default_mappings", True):
        for form_field, anki_field in DEFAULT_FIELD_MAPPINGS.items():
            if anki_field in card_info:
                params[form_field] = card_info[anki_field]
            elif anki_field in card_info.get("fields", {}):
                params[form_field] = card_info["fields"][anki_field]
    else:
        # Add known form fields from config
        for field, entry_id in config["form_fields"].items():
            if entry_id and field in card_info:
                params[entry_id] = card_info[field]
    
    # Construct the URL with parameters
    url = config["google_form_url"]
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    # Open the Google Form in the default browser
    openLink(url)
    
    # Show a confirmation message
    showInfo("Thank you for reporting this card. A browser window has been opened with the form.")

def setup_menu_and_hotkey():
    """Set up the menu item and hotkey for reporting incorrect tags."""
    # Create a new menu item in the Tools menu
    action = QAction("Report Incorrect Tags", mw)
    
    # Set the keyboard shortcut
    action.setShortcut(QKeySequence(config["hotkey"]))
    
    # Connect the action to our function
    action.triggered.connect(report_incorrect_tag)
    
    # Add the action to the Tools menu
    mw.form.menuTools.addAction(action)
    
    # Create a configuration menu item
    config_action = QAction("Configure Tag Reporter", mw)
    config_action.triggered.connect(lambda: config_dialog())
    mw.form.menuTools.addAction(config_action)
    
    # Check if this is the first run
    if config.get("first_run", True):
        # Schedule the first run setup to run after Anki has fully loaded
        mw.progress.timer(1000, first_run_setup, False)

def config_dialog():
    """Show a dialog to configure the add-on."""
    # Load the latest config
    global config
    config = load_config()
    
    # Create a dialog
    dialog = QDialog(mw)
    dialog.setWindowTitle("Configure Incorrect Tags Reporter")
    dialog.setMinimumWidth(400)
    
    # Create layout
    layout = QVBoxLayout()
    dialog.setLayout(layout)
    
    # Form layout for settings
    form_layout = QFormLayout()
    
    # Google Form URL
    url_input = QLineEdit(config["google_form_url"])
    form_layout.addRow("Google Form URL:", url_input)
    
    # Hotkey
    hotkey_input = QLineEdit(config["hotkey"])
    form_layout.addRow("Hotkey:", hotkey_input)
    
    # Use default Mount Sinai mappings
    use_default_mappings_checkbox = QCheckBox()
    use_default_mappings_checkbox.setChecked(config.get("use_default_mappings", True))
    form_layout.addRow("Use Mount Sinai default field mappings:", use_default_mappings_checkbox)
    
    # Form fields (collapsible section)
    form_fields_group = QGroupBox("Form Field IDs (Advanced)")
    form_fields_layout = QFormLayout()
    form_fields_group.setLayout(form_fields_layout)
    
    field_inputs = {}
    for field, entry_id in config["form_fields"].items():
        field_inputs[field] = QLineEdit(entry_id)
        form_fields_layout.addRow(f"{field}:", field_inputs[field])
    
    # Add layouts to main layout
    layout.addLayout(form_layout)
    layout.addWidget(form_fields_group)
    
    # Help text
    help_label = QLabel("""
    <p>To find your Google Form field IDs:</p>
    <ol>
        <li>Go to your Google Form</li>
        <li>Right-click and select "View Page Source"</li>
        <li>Search for "entry." in the source code</li>
        <li>Look for IDs like "entry.123456789"</li>
    </ol>
    <p><b>Note:</b> If you're from Mount Sinai, you can check "Use Mount Sinai default field mappings" 
    to automatically populate the form fields using the predefined mappings.</p>
    """)
    help_label.setWordWrap(True)
    layout.addWidget(help_label)
    
    # Buttons
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)
    
    # Show dialog
    if dialog.exec_():
        # Save settings
        config["google_form_url"] = url_input.text()
        config["hotkey"] = hotkey_input.text()
        config["use_default_mappings"] = use_default_mappings_checkbox.isChecked()
        
        for field in config["form_fields"]:
            config["form_fields"][field] = field_inputs[field].text()
        
        save_config(config)
        
        showInfo("Configuration saved. Please restart Anki for some changes to take effect.")

# Add the menu item and hotkey when Anki starts
addHook("profileLoaded", setup_menu_and_hotkey)
