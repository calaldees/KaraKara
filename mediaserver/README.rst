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



Router Setup
~~~~~~~~~~~~

Netgear routers
 172.20.1.1
  channel 1
  points to 172.20.1.2 for dhcp
  172.20.1.2 reserved for ethernet mac address
  subnet mask of 255.255.0.0
 172.20.12.1 -

Wireless
 SSID: Karakara
 b & g
 no encryption
 primary dns: 172.20.1.2
LAN
 DCHP off
 subnet 255.255.0.0
 set range dchp range to off but include 172.20.x.3 > 254

Ubuntu ethernet setup
 do not automaticall connect
 Manual 172.20.1.2 subnet 255.255.0.0 gateway 0.0.0.0
 Require ipv4 to complete + route + use this connetion for resorces on this network only

Old satilte laptop
172.20.1.2	ALLAN-SATELLITE-PRO-L300D	00:1E:33:C0:4C:D2
