"""

"""


class TraversalGlobalRootFactory():
    def __init__(self, request):
        pass

    def __getitem__(self, key):
        return {
            #'queue': QueueContext(),
            'track': TrackContext(parent=self),  # Admin only for all tracks
            #'track_list': TrackListContext(),  # Admin only for all tracks
            #'comunity': ComunityContext(),
            #'track_import': TrackImportContext(),  # Needs secure permissions
        }[key]


class QueueContext():
    name = 'queue'

    def __getitem__(self, key):
        return {
            'track': TrackContext(),
            'track_list': TrackListContext(),
        }[key]


class TrackContext():
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
    pass


class TrackImportContext():
    pass
