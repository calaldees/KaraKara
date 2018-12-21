<%inherit file="_base.mako"/>

<form action="" style="max-width: 20em; margin: auto;">
    <label id="input_queue_label" for="input_queue">${_('mobile.home.input_queue_label')}</label>
    <input id="input_queue" type="text" name="queue_id" />
    <input type="submit" value="${_('mobile.home.join_label')}" />
</form>
