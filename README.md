# Directory data to csv
Are you ever unsure what files are on in a folder on your computer or network drive? Small folders are easy to click and see, but large folders with many subfolders can be too much to look through.

Using Python, I made a script to walk through a file directory and output the data in an easy to read tabular format.
# Tkinter GUI
I added a basic GUI using Tkinter. Tkinter has a file dialogue that works for selecting a folder. The user has the option to specify how far down the directory to see. The user also can toggle if file names in the folders will be included in the output.
# Output
The output includes the path, folder/file name, count of files and folders both in that folder and subfolders, and a list of file types sorted by occurrence. A list of files in the folders can also be added to the list. The output is saved as a csv file. The output file name is based on the name of the directory, so the script can be ran for multiple directories without overwriting other searches. 
