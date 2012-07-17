A standalone Python 2.x script to run on a general webserver to allow non specalists to contibute to track taging

--------------------------------------

Magic commands that are helpful when using this script:

find -iname '*.txt' -print0 | xargs -0 tar -zcf - | ssh calaldees@calaldees.dreamhosters.com "(cd calaldees.dreamhosters.com/karakara/data; tar zxf -)"

http://www.lamolabs.org/blog/1766/pushing-pulling-files-around-using-tar-ssh-scp-rsync/
http://superuser.com/questions/299448/linux-compressing-all-pdf-files-recursively-tar

rsync --------------------------------

ssh calaldess@calaldees.dreamhosters.com

Up
rsync -e ssh -av local_directory username@server.dreamhost.com:remote_directory
--delete --update --inplace --stats --compress

down
rsync -e ssh -av username@server.dreamhost.com:remote_directory local_directory 
--inplace --update --stats --compress


http://wiki.dreamhost.com/Rsync
http://wiki.dreamhost.com/Rsync_Backup
http://samba.anu.edu.au/ftp/rsync/rsync.html


