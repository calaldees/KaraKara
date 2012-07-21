A standalone Python 2.x script to run on a general webserver to allow non specalists to contibute to track taging

--------------------------------------

Magic commands that are helpful when using this script:

find -iname '*.txt' -print0 | xargs -0 tar -zcf - | ssh calaldees@calaldees.dreamhosters.com "(cd calaldees.dreamhosters.com/karakara/data; tar zxf -)"

http://www.lamolabs.org/blog/1766/pushing-pulling-files-around-using-tar-ssh-scp-rsync/
http://superuser.com/questions/299448/linux-compressing-all-pdf-files-recursively-tar

rsync calaldees@calaldees.dreamhosters.com:calaldees.dreamhosters.com/karakara/data/ /home/allan/code/KaraKara/mediaserver/www/files/ -e ssh --archive --verbose --update --inplace --stats --compress

rsync --------------------------------

ssh calaldess@calaldees.dreamhosters.com


to test - add params
--verbose --dry-run (or add the letters 'vn' to the param list)

Up
rsync local_directory username@server.dreamhost.com:remote_directory -e ssh --archive --verbose --update --inplace --stats --compress --delete

down
rsync username@server.dreamhost.com:remote_directory local_directory -e ssh --archive --verbose --update --inplace --stats --compress


http://wiki.dreamhost.com/Rsync
http://wiki.dreamhost.com/Rsync_Backup
http://samba.anu.edu.au/ftp/rsync/rsync.html


