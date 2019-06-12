from pyramid.view import view_config

from . import action_ok, action_error, community_only, is_community

from .queue_settings import queue_settings_view_put, acquire_cache_bucket_func, REGISTRY_SETTINGS_PASSTHROUGH, SETTINGS_ADMIN_EXTRA_EXPOSE


@view_config(
    context='karakara.traversal.CommunitySettingsContext',
    request_method='GET',
)
@community_only
def community_settings_view(request):
    if not request.context.queue_id:
        raise action_error('queue_id required')

    return action_ok(data={'settings': {
        **{key: '' for key in SETTINGS_ADMIN_EXTRA_EXPOSE},
        **{
            key: value
            for key, value in request.queue.settings.items()
            if key not in REGISTRY_SETTINGS_PASSTHROUGH
        },
    }})


@view_config(
    context='karakara.traversal.CommunitySettingsContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
#    request_method='POST',
    method_router='PUT',
)
@community_only
def community_settings_put(request):
    if not request.context.queue_id:
        raise action_error('queue_id required')

    return queue_settings_view_put(request)
    #raise action_error('not implemented')
