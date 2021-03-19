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
                #TrackContext,  # Admin only for all tracks
                #TrackListContext,  # Admin only for all tracks
                CommunityContext,
                TrackImportContext,  # Needs secure permissions
                MQTTContext,
            )
        )


class QueueResourceMixin():
    @property
    def queue_context(self):
        return pyramid.traversal.find_interface(self, QueueContext)

    @property
    def queue_id(self):
        try:
            return self.queue_context.id
        except AttributeError:
            pass


class QueueContext(QueueResourceMixin, NextContextMixin):
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
                    SearchListContext,
                    SearchTagsContext,
                    RandomImagesContext,
                    RemoteControlContext,
                    QueueAdminContext,
                    QueuePriorityTokenContext,
                )
            )
        return QueueContext(parent=self, id=key)


class QueueItemsContext(QueueResourceMixin):
    __template__ = 'queue_items'
    __name__ = 'queue_items'

    def __init__(self, parent=None):
        self.__parent__ = parent


class QueueSettingsContext(QueueResourceMixin):
    __template__ = 'queue_settings'
    __name__ = 'settings'

    def __init__(self, parent=None):
        self.__parent__ = parent


class TrackContext(QueueResourceMixin):
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


class SearchListContext(QueueResourceMixin):
    __template__ = 'queue_search_list'
    __name__ = 'search_list'

    def __init__(self, parent=None):
        self.__parent__ = parent
        self.tags = []

    def __getitem__(self, key):
        self.tags.append(key)
        return self


class SearchTagsContext(QueueResourceMixin):
    __template__ = 'queue_search_tags'
    __name__ = 'search_tags'

    def __init__(self, parent=None):
        self.__parent__ = parent
        self.tags = []

    def __getitem__(self, key):
        self.tags.append(key)
        return self


class RandomImagesContext(QueueResourceMixin):
    __template__ = 'queue_random_images'
    __name__ = 'random_images'

    def __init__(self, parent=None):
        self.__parent__ = parent


class RemoteControlContext(QueueResourceMixin):
    __template__ = 'queue_remote_control'
    __name__ = 'remote_control'

    def __init__(self, parent=None):
        self.__parent__ = parent


class QueueAdminContext(QueueResourceMixin):
    __template__ = 'queue_admin'
    __name__ = 'admin'

    def __init__(self, parent=None):
        self.__parent__ = parent


class QueuePriorityTokenContext(QueueResourceMixin):
    __template__ = 'queue_priority_tokens'
    __name__ = 'priority_tokens'

    def __init__(self, parent=None):
        self.__parent__ = parent


class TrackListContext(QueueResourceMixin):
    __template__ = 'track_list'
    __name__ = 'track_list'

    def __init__(self, parent=None):
        self.__parent__ = parent


class CommunityContext(NextContextMixin):
    __template__ = 'community'
    __name__ = 'community'

    def __init__(self, parent=None):
        self.__parent__ = parent

    def __getitem__(self, key):
        return self.next_context(
            key,
            (
                CommunityLoginContext,
                CommunityLogoutContext,
                CommunityListContext,
                CommunityTrackContext,
                CommunityUploadContext,
                CommunitySettingsContext,
                CommunityProcessmediaLogContext,
                CommunityQueueContext,
                CommunityUsersContext,
                CommunityQueueItemsContext,
            )
        )


class CommunityLoginContext():
    __template__ = 'community_login'
    __name__ = 'login'

    def __init__(self, parent=None):
        self.__parent__ = parent


class CommunityLogoutContext():
    __template__ = 'community_logout'
    __name__ = 'logout'

    def __init__(self, parent=None):
        self.__parent__ = parent


class CommunityListContext():
    __template__ = 'community_list'
    __name__ = 'list'

    def __init__(self, parent=None):
        self.__parent__ = parent


class CommunityTrackContext():
    __template__ = 'community_track'
    __name__ = 'track'

    def __init__(self, parent=None, id=None):
        self.__parent__ = parent
        self.id = id
        if self.id:
            self.__name__ = self.id

    def __getitem__(self, key):
        if self.id:
            raise KeyError()
        return CommunityTrackContext(parent=self, id=key)


class CommunityUploadContext():
    __template__ = 'community_upload'
    __name__ = 'upload'

    def __init__(self, parent=None):
        self.__parent__ = parent


class QueueIdMixin():
    def __init__(self, parent=None, id=None):
        self.__parent__ = parent
        self.id = id
        if self.id:
            self.__name__ = self.id

    def __getitem__(self, key):
        if self.id:
            raise KeyError()
        return self.__class__(parent=self, id=key)

    @property
    def queue_id(self):
        return self.id


class CommunityQueueItemsContext(QueueIdMixin):
    __template__ = 'community_queue_items'
    __name__ = 'queue_items'


class CommunitySettingsContext(QueueIdMixin):
    __template__ = 'community_settings'
    __name__ = 'settings'


class CommunityProcessmediaLogContext():
    __template__ = 'community_processmedia_log'
    __name__ = 'processmedia_log'

    def __init__(self, parent=None):
        self.__parent__ = parent


class CommunityQueueContext():
    __template__ = 'community_queues'
    __name__ = 'queues'

    def __init__(self, parent=None):
        self.__parent__ = parent


class CommunityUsersContext():
    __template__ = 'community_users'
    __name__ = 'users'

    def __init__(self, parent=None):
        self.__parent__ = parent


class TrackImportContext():
    __name__ = 'track_import'

    def __init__(self, parent=None):
        self.__parent__ = parent


class MQTTContext(NextContextMixin):
    __name__ = '_mqtt'

    def __init__(self, parent=None):
        self.__parent__ = parent

    def __getitem__(self, key):
        return self.next_context(
            key,
            (
                MQTTUserContext,
                MQTTAclContext,
            )
        )

class MQTTUserContext():
    __name__ = 'user'

    def __init__(self, parent=None):
        self.__parent__ = parent
