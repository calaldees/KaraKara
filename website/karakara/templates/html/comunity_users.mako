<%inherit file="_base_comunity.mako"/>

<%def name="body()">
	<h2>Comunity Users</h2>

	<script>
		function submit_approved(that) {
			var form = $(that).parent();
			var $form = $(form);
			console.log('submit_approved', form);
			$form.submit(function(event) {
				$.ajax({
					type: 'POST',
					url: form.action,
					data: $form.serialize(),
					dataType: 'json',
					encode: true
				}).done(function(data) {
					console.log('submit_approved', '.done', data);
				});
				event.preventDefault();
			});
			form.submit();
		}
	</script>

	<table id="user_list" class="table table-condensed table-hover">
		<tr><th>name</th><th>email</th><th>approved</th></tr>
		% for user in data.get('users', []):
			${user_row(user)}
		% endfor
	</table>
</%def>

<%def name="user_row(user)">
	<tr>
		<td>${user.get('name')}</td>
		<td>${user.get('email')}</td>
		<td>
			<form action="" method="POST">
				<input type="checkbox" name="approved" value="true" onchange="submit_approved(this);"
				% if user.get('approved'):
				checked
				% endif
				/>
				<input type="hidden" name="user_id" value="${user.get('id')}" />
			</form>
		</td>
	</tr>
</%def>