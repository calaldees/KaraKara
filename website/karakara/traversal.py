"""

"""
import pyramid.traversal


class TraversalGlobalRootFactory():
    __template__ = 'home'
    __name__ = ''

    def __init__(self, request):
        pass

    def __getitem__(self, key):
        return {
            'queue': QueueContext,
            'track': TrackContext,  # Admin only for all tracks
            'track_list': TrackListContext,  # Admin only for all tracks
            #'comunity': ComunityContext(),
            #'track_import': TrackImportContext(),  # Needs secure permissions
        }[key](parent=self)


class KaraKaraResourceMixin():
    @property
    def queue_id(self):
        queue_context = pyramid.traversal.find_interface(self, QueueContext)
        if queue_context:
            return queue_context.id
        return None


class QueueContext():
    __template__ = 'queue_home'
    __name__ = 'queue'

    def __init__(self, parent=None, id=None):
        self.__parent__ = parent
        self.id = id
        if self.id:
            self.__name__ = self.id

    def __getitem__(self, key=None):
        if self.id:
            return {
                'track': TrackContext,
                'track_list': TrackListContext,
                'queue_items': QueueItemsContext,
            }[key](parent=self)
        return QueueContext(parent=self, id=key)


class QueueItemsContext():
    __template__ = 'queue_items'
    __name__ = 'queue_items'

    def __init__(self, parent=None):
        self.__parent__ = parent


class TrackContext(KaraKaraResourceMixin):
    __template__ = 'track'
    __name__ = 'track'

    def __init__(self, parent=None, id=None):
        self.__parent__ = parent
        self.id = id
        if self.id:
            self.__name__ = self.id

    def __getitem__(self, key):
        if self.id:
            raise KeyError()
        return TrackContext(parent=self, id=key)


class ComunityContext():
    __template__ = 'comunity'


class TrackListContext():
    __template__ = 'track_list'

    def __init__(self, parent=None):
        self.__parent__ = parent


class TrackImportContext():
    pass
