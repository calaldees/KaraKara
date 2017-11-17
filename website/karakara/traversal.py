"""

"""
import pyramid.traversal


class TraversalGlobalRootFactory():
    def __init__(self, request):
        pass

    def __getitem__(self, key):
        return {
            'queue': QueueContext(parent=self),
            'track': TrackContext(parent=self),  # Admin only for all tracks
            #'track_list': TrackListContext(),  # Admin only for all tracks
            #'comunity': ComunityContext(),
            #'track_import': TrackImportContext(),  # Needs secure permissions
        }[key]


class KaraKaraResourceMixin():
    @property
    def queue_id(self):
        queue_context = pyramid.traversal.find_interface(self, QueueContext)
        if queue_context:
            return queue_context.id
        return None


class QueueContext():
    name = 'queue'

    def __init__(self, parent=None, id=None):
        self.__parent__ = parent
        self.id = id

    def __getitem__(self, id=None):
        if self.id:
            return {
                'track': TrackContext(parent=self),
                'track_list': TrackListContext(parent=self),
            }[id]
        return QueueContext(parent=self, id=id)


class TrackContext(KaraKaraResourceMixin):
    name = 'track'

    def __init__(self, parent=None, id=None):
        self.__parent__ = parent
        self.id = id

    def __getitem__(self, id):
        if self.id:
            raise KeyError()
        return TrackContext(parent=self, id=id)


class ComunityContext():
    name = 'comunity'


class TrackListContext():
    def __init__(self, parent=None):
        self.__parent__ = parent


class TrackImportContext():
    pass
