<%inherit file="_base.mako"/>

<form action="" onsubmit="store_performer_name();">
    <label id="input_queue_label" for="input_queue">${_('mobile.home.input_queue_label')}</label>
    <input id="input_queue" type="text" name="queue_id" />
    <label id="input_performer_name_label" for="input_performer_name">${_('mobile.home.input_performer_name_label')}</label>
    <input id="input_performer_name" type="text" name="performer_name" />
</form>
