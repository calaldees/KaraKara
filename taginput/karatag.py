#!/usr/bin/python

import cgi      # For accessing web form data
import cgitb    # If there is an error in the script show it as an HTML page for web debugging
cgitb.enable()            # Enable web debugging
form = cgi.FieldStorage() # Get web form data as form

import os, urllib, datetime

name   = __file__.split('.')[0]

path_root = './data/'
path_tags = 'tags.txt'
time_limit = datetime.datetime(year=2012, month=7, day=1)

#----------------------------------------------------------------------------------

def id_to_filename(id):
	return os.path.join(path_root,id,path_tags)
def filename_to_id(filename):
	return filename.replace(path_root,'').replace("/%s"%path_tags,'')

def print_file(filename):
	print("<pre>")
	file = open(filename,'r')
	for line in file:
		print(line.replace('\n',''))
        file.close()
	print("</pre>")

def html_doc(func_body, title=''):
	print("Content-type: text/html") # Required for web server output
	print("")                        # Required for web server output
	print("<html><head>")
	print("  <title>%s</title>" % title)
	print("  <link type='text/css' href='%s.css' rel='stylesheet'/>" % name)
	print("</head><body>")
	print("")
	print("<div class='tag_description'>")
	print_file('karatags.txt')
	print("</div>")
	print("")
	func_body()
	print("")
	print("</body></html>")

def tag_link(id, text=None):
	time_mod = datetime.datetime.fromtimestamp(os.path.getmtime(id_to_filename(id)))
	class_   = ''
	if not text:
		text = id
	if time_mod > time_limit:
		class_ = 'edited'
	return "<a href='%(script)s?id=%(id)s' class='%(class_)s'>%(text)s</a>" % dict(script=__file__, id=urllib.quote(id), text=text, class_=class_)

def list_all():
	for root, dirs, files in os.walk(path_root):
		for file in files:
			print("<p>%s</p>" % tag_link(filename_to_id(os.path.join(root,file))) )

def edit_tags(id):
	print("<h1>%s</h1>" % id)
	print("<a href='http://192.168.1.69:8000/files/%s/preview/0_generic.mp4' target='_blank'>video preview</a>" % urllib.quote(id) )
	
	if 'tag_data' in form:
		file = open(id_to_filename(id), 'w')
		file.write(form['tag_data'].value)
		file.close()
	
	print("<form action='' method='POST'>")
	print("<input type='hidden' name='id' value=\"%s\">" % id)
	file = open(id_to_filename(id), 'r')
	tag_data = file.read()
	file.close()
	print("<textarea name='tag_data'>%s</textarea>" % tag_data)
	print("<br/><input type='submit'>")
	print("</form>")
	
	if 'tag_data' in form:
		print("<p>Saved</p>")
	
def main():
	func_body = list_all
	if 'id' in form:
		func_body = lambda: edit_tags(form['id'].value)
	html_doc(func_body, title='KaraKara Tag')

if __name__ == "__main__":
  main()
