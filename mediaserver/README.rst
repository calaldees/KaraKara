Notes
~~~~~
Scripts to install/setup/run a lightweight HTTP sever to serve the processed
static media files

./www/files/ will be presented as /files/

accessing the root directory of the web site will proxy to pylons

processmedia will place all processed files in the folder served by this service

(todo: DCHP server setup. to be in separate folder)

Local IPs (of known services) should have access to
- File/Folder lists
- All static files

Remote IPs should have access to
- Just images and preview files
- No file/folder lists
- No full videos
- No subtilte files

Running the server
~~~~~~~~~~~~~~~~~~
- `make run` to run the server
- Ctrl-C to stop it
