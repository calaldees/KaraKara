#from pyramid.view import view_config

#from . import web, action_ok

#from externals.lib.pyramid.views.upload import Upload
#@view_config(route_name='upload')
#@web
#def upload(request):
#    return action_ok()

import os
import re
import shutil

from pyramid.view import view_config, view_defaults
import pyramid.response

import logging
log = logging.getLogger(__name__)


WEBSITE = 'http://blueimp.github.io/jQuery-File-Upload/'
MIN_FILE_SIZE =   1 * 1000 * 1000  # 1mb - A video smaller than that is not worth having
MAX_FILE_SIZE = 100 * 1000 * 1000  # 100Mb
#IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
#ACCEPT_FILE_TYPES = IMAGE_TYPES
EXPIRATION_TIME = 300  # seconds

DELETEMETHOD = 'DELETE'



@view_defaults(route_name='upload')
class Upload():
    """
    Pyramid route class that supports segmented file upload from jQuery-File-Upload
    https://github.com/blueimp/jQuery-File-Upload/wiki/
    
    HTML 5 Spec refernce
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.16
    
    https://github.com/blueimp/jQuery-File-Upload/wiki/Chunked-file-uploads
     - The byte range of the blob is transmitted via the Content-Range header.
     - The file name of the blob is transmitted via the Content-Disposition header.
     
    http://stackoverflow.com/questions/21352995/how-to-handle-file-upload-asynchronously-in-pyramid
    """
    
    def __init__(self, request):
        self.request = request
        request.response.headers['Access-Control-Allow-Origin'] = '*'
        request.response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
        request.response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Content-Range, Content-Disposition'

    def _path_upload(self, filename=''):
        return os.path.join(self.request.registry.settings.get('upload.path','upload'), filename)

    def _get_file_size(self, file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    def _validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        #elif not ACCEPT_FILE_TYPES.match(file['type']):
        #    file['error'] = 'Filetype not allowed'
        else:
            return True
        return False

    @view_config(request_method='OPTIONS')
    def options(self):
        log.info('options')
        return pyramid.response.Response(body='')

    @view_config(request_method='HEAD')
    def head(self):
        log.info('head')
        return pyramid.response.Response(body='')

    @view_config(request_method='GET', renderer="json")
    def get(self):
        log.info('get')
        filename = self.request.matchdict.get('name')
        return [f for f in os.listdir(self._path_upload())]

    @view_config(request_method='DELETE', xhr=True, accept="application/json", renderer='json')
    def delete(self):
        log.info('delete')
        filename = self.request.matchdict.get('name')
        try:
            os.remove()
        except IOError:
            return False
        return True
    
    @view_config(request_method='POST', xhr=True, accept="application/json", renderer='json')
    def post(self):
        log.info('post')
        if self.request.matchdict.get('_method') == "DELETE":
            return self.delete()
        results = []
        for name, fieldStorage in self.request.POST.items():
            if not hasattr(fieldStorage, 'filename'):
                continue
            result = {}
            result['name'] = os.path.basename(fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self._get_file_size(fieldStorage.file)
            if self._validate(result):
                #with open( self.imagepath(result['name'] + '.type'), 'w') as f:
                #    f.write(result['type'])
                with open( self._path_upload(result['name']), 'wb') as f:
                    shutil.copyfileobj( fieldStorage.file , f)
                #self.createthumbnail(result['name'])

                result['delete_type'] = DELETEMETHOD
                result['delete_url'] = self.request.route_url('upload', spacer='.', name='', format='json') + '/' + result['name']
                result['url'] = self.request.route_url('comunity', name=result['name'], spacer='.', format='json')
                if DELETEMETHOD != 'DELETE':
                    result['delete_url'] += '&_method=DELETE'
                #if (IMAGE_TYPES.match(result['type'])):
                #    try:
                #        result['thumbnail_url'] = self.thumbnailurl(result['name'])
                #    except: # Could not get an image serving url
                #        pass
            results.append(result)
        return {'files': results}
