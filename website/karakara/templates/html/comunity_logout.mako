<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <p>Logged out</p>
</%def>

<%def name="scripts_inline()">
    // Mozilla Persona Logout
    if (typeof(navigator) != "undefined") {
        navigator.id.logout();
    }
</%def>