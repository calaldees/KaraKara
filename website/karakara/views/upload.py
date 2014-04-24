#from pyramid.view import view_config

#from . import web, action_ok

#from externals.lib.pyramid.views.upload import Upload
#@view_config(route_name='upload')
#@web
#def upload(request):
#    return action_ok()


from pyramid.view import view_config, view_defaults
import pyramid.response
import os


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

    def path_upload(self, filename=''):
        return os.path.join(self.request.registry.settings.get('upload.path','upload'), filename)

    @view_config(request_method='OPTIONS')
    def options(self):
        return pyramid.response.Response(body='')

    @view_config(request_method='HEAD')
    def head(self):
        return pyramid.response.Response(body='')

    @view_config(request_method='GET', renderer="json")
    def get(self):
        filename = self.request.matchdict.get('name')
        return [f for f in os.listdir(self.path_upload())]

    @view_config(request_method='DELETE', xhr=True, accept="application/json", renderer='json')
    def delete(self):
        filename = self.request.matchdict.get('name')
        try:
            os.remove()
        except IOError:
            return False
        return True
    
    @view_config(request_method='POST', xhr=True, accept="application/json", renderer='json')
    def post(self):
        if self.request.matchdict.get('_method') == "DELETE":
            return self.delete()
        results = []
        for name, fieldStorage in self.request.POST.items():
            if not hasattr(fieldStorage, 'filename'):
                continue
            result = {}
            result['name'] = os.path.basename(fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                with open( self.imagepath(result['name'] + '.type'), 'w') as f:
                    f.write(result['type'])
                with open( self.imagepath(result['name']), 'w') as f:
                    shutil.copyfileobj( fieldStorage.file , f)
                self.createthumbnail(result['name'])

                result['delete_type'] = DELETEMETHOD
                result['delete_url'] = self.request.route_url('imageupload',sep='',name='') + '/' + result['name']
                result['url'] = self.request.route_url('imageview',name=result['name'])
                if DELETEMETHOD != 'DELETE':
                    result['delete_url'] += '&_method=DELETE'
                if (IMAGE_TYPES.match(result['type'])):
                    try:
                        result['thumbnail_url'] = self.thumbnailurl(result['name'])
                    except: # Could not get an image serving url
                        pass
            results.append(result)
        return results
