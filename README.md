# Dupe Hunter

Finds duplicate files.  

For speed, the program first finds files with matching sizes. It then runs an MD5 hash against this shortlist to find duplicate files.  

Optionally (with the `-d` flag), it will prompt you to delete one of the duplicates. 

&nbsp;

## Setup
`pip3 install -r requirements.txt`  
&nbsp;

## Use
`-p /path` - Specify a filesystem path to recursively scan  
`-s scanlist.txt` -  (Optional) A text file containing a list of file extensions  
`-d yes` - (Optional) Prompt to delete duplicate files  
&nbsp;

## Examples
`./dupehunter.py -p ~/Dropbox`  
`./dupehunter.py -p ~/Pictures -s scanlist.txt -d yes`  