#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import customtkinter as ctk
from tkinter import filedialog
import json
import os
import shutil
from pathlib import Path
from itertools import chain

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTIONS:
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Strip Deletion Function
def delete_strip(frame, entries):
    frame.destroy()  # Removes the frame and its contents
    strips.remove(entries)  # Remove the reference to this strip's entries

# Directory Browsing Function
def browse_directory(entry_widget):
    directory = filedialog.askdirectory()
    if directory:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, directory)

# Strip Creation Function
def add_strip(path_value="", filetypes_value="", tags_value=""):
# Label Strip Frame
    strip = ctk.CTkFrame(strip_frame)
    strip.pack(pady=5, padx=10, fill="x")
# Directory Path Label
    path_label = ctk.CTkLabel(strip, text="Directory Path:")
    path_label.pack(side="left", padx=5)
# Entry widget for directory path
    path_entry = ctk.CTkEntry(strip, placeholder_text="Select Directory")
    path_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
    path_entry.insert(0, path_value)  # Preload value if provided
# Button to browse for directory
    browse_btn = ctk.CTkButton(strip, text="Browse", width=70, command=lambda: browse_directory(path_entry),fg_color="#707070")
    browse_btn.pack(side="left", padx=5)
# Label for file types
    filetype_label = ctk.CTkLabel(strip, text="File Types:")
    filetype_label.pack(side="left", padx=5)
# Entry widget for file types (comma-separated)
    filetype_entry = ctk.CTkEntry(strip, placeholder_text="e.g., *.png, *.txt")
    filetype_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
    filetype_entry.insert(0, filetypes_value)  # Preload value if provided

# Label for tags
    tags_label = ctk.CTkLabel(strip, text="Tags:")
    tags_label.pack(side="left", padx=5)

# Entry widget for tags (comma-separated)
    tags_entry = ctk.CTkEntry(strip, placeholder_text="e.g., project, work")
    tags_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
    tags_entry.insert(0, tags_value)  # Preload value if provided

# Store references to the path and file types
    strips.append({"path_entry": path_entry, "filetype_entry": filetype_entry,"tags_entry":tags_entry})
# Create a delete button to remove the strip
    delete_btn = ctk.CTkButton(strip, text="Delete", width=70, command=lambda: delete_strip(strip, strips[-1]),fg_color="#8a473e")
    delete_btn.pack(side="left", padx=5, pady=5)

# Function to save the current configuration to a file
def save_config():
    data = []
    for strip in strips:
        path_value = strip["path_entry"].get()
        filetypes_value = strip["filetype_entry"].get()
        tags_value = strip["tags_entry"].get()
        data.append({"directory": path_value, "filetypes": filetypes_value, "tags":tags_value})

    with open(config_file, "w") as f:
        json.dump(data, f, indent=4)
    print("Configuration saved.")

# Function to run the gui logic that sorts out Desktop / Downloads folder
def organize():
    # Get the desktop directory
    desktop_path = Path(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))
    download_path = Path(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads'))
    # Loop through all files on the desktop
    for file in chain(desktop_path.iterdir(), download_path.iterdir()):
        if file.is_file():
            filename = file.name
            moved = False  # Track if the file has been moved

            # Check against each strip
            for strip in strips:
                target_dir = Path(strip["path_entry"].get())
                if not target_dir.exists():
                    print(f"Target directory does not exist: {target_dir}")
                    continue

                # Get the file types and tags, ensuring they're stripped of whitespace
                filetypes = [ext.strip().lower() for ext in strip["filetype_entry"].get().split(",") if ext.strip()]
                tags = [tag.strip().lower() for tag in strip["tags_entry"].get().split(",") if tag.strip()]

                # Debugging output to show current checks
                print(f"Checking file: {filename}, against tags: {tags}, filetypes: {filetypes}")

                # Check if the file matches any of the tags
                if any(tag.replace('*', '') in filename.lower() for tag in tags):  # Remove wildcard from tags for matching
                    print(f"Moving file by tag: {file} -> {target_dir}")
                    shutil.move(str(file), target_dir)
                    moved = True  # Mark as moved
                    break  # Skip the rest of the loop since the file has been moved

                # Check if the file matches any of the file extensions
                if any(filename.lower().endswith(ext.replace('*', '').strip()) for ext in filetypes):  # Remove wildcards for matching
                    print(f"Moving file by extension: {file} -> {target_dir}")
                    shutil.move(str(file), target_dir)
                    moved = True  # Mark as moved
                    break  # Skip the rest of the loop since the file has been moved

            if not moved:
                print(f"No matching criteria for file: {file}")

    print("Organizing completed.")

# Function to load the configuration from a file
def load_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            data = json.load(f)
            for item in data:
                add_strip(item["directory"], item["filetypes"], item["tags"])
        print("Configuration loaded.")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Window Config
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Path to save the configuration
config_file = "config.json"

# Initialize the main app window
app = ctk.CTk()
app.geometry("1000x800")
app.title("File organizer 1.0")
app.iconbitmap("icon.ico")

buttons= ctk.CTkFrame(app)

# Label Strip Button
add_strip_btn = ctk.CTkButton(buttons, text="Add Directory", command=add_strip,fg_color="#65417a")
add_strip_btn.grid(column=5,row=0,padx=5,pady=5)

# Button for saving files to config.json
save_btn = ctk.CTkButton(buttons, text="Save Config", command=save_config,fg_color="#65417a")
save_btn.grid(column=4,row=0,padx=5,pady=5)

# Button that sorts the files
sort_btn = ctk.CTkButton(buttons, text="Organize", command=organize,fg_color="#65417a")
sort_btn.grid(column=3,row=0,padx=5,pady=5)

buttons.pack(pady=5,side=ctk.TOP, fill=ctk.X)

# Frame to hold strips
strip_frame = ctk.CTkFrame(app)
strip_frame.pack(pady=5, fill="both", expand=True)

# List to store references to entry widgets for paths and file types
strips = []

# Load the config when the app starts
load_config()

# Run the main loop
app.mainloop()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~