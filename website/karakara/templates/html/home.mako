<%inherit file="_base.mako"/>


<label id="input_queue_label" for="input_queue">${_('mobile.home.input_queue_label')}</label>
<input id="input_queue" type="text" name="queue" onkeydown="if (event.keyCode==13) {console.log(window.location);}"/>
