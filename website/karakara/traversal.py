"""

"""
import pyramid.traversal


class NextContextMixin():
    def next_context(self, key, context_classs):
        return {
            context_class().__name__: context_class  # TODO: Help?! I need to instantiate context_class to get it's __name__, else __name__ is the ClassName .. which I do not want!!
            for context_class in context_classs
        }[key](parent=self)


class TraversalGlobalRootFactory(NextContextMixin):
    __template__ = 'home'
    __name__ = ''

    def __init__(self, request):
        pass

    def __getitem__(self, key):
        return self.next_context(
            key,
            (
                QueueContext,
                TrackContext,  # Admin only for all tracks
                TrackListContext,  # Admin only for all tracks
                #ComunityContext
                #TrackImportContext # Needs secure permissions
            )
        )


class KaraKaraResourceMixin():
    @property
    def queue_context(self):
        return pyramid.traversal.find_interface(self, QueueContext)

    @property
    def queue_id(self):
        try:
            return self.queue_context.id
        except AttributeError:
            pass


class QueueContext(KaraKaraResourceMixin, NextContextMixin):
    __template__ = 'queue_home'
    __name__ = 'queue'

    def __init__(self, parent=None, id=None):
        self.__parent__ = parent
        self.id = id
        if self.id:
            self.__name__ = self.id

    def __getitem__(self, key=None):
        if self.id:
            return self.next_context(
                key,
                (
                    TrackContext,
                    TrackListContext,
                    QueueItemsContext,
                    QueueSettingsContext,
                )
            )
        return QueueContext(parent=self, id=key)


class QueueItemsContext(KaraKaraResourceMixin):
    __template__ = 'queue_items'
    __name__ = 'queue_items'

    def __init__(self, parent=None):
        self.__parent__ = parent


class QueueSettingsContext(KaraKaraResourceMixin):
    __template__ = 'queue_settings'
    __name__ = 'settings'

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
    __name__ = 'comunity'


class TrackListContext():
    __template__ = 'track_list'
    __name__ = 'track_list'

    def __init__(self, parent=None):
        self.__parent__ = parent


class TrackImportContext():
    pass
