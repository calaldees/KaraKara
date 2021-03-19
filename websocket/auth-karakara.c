//
// Based a lot on:
// https://github.com/hadleyrich/mosquitto-auth-plugin-http
// Copyright 2014 Hadley Rich, nice technology Ltd.
// Website: http://nice.net.nz
// MIT license
//

#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <curl/curl.h>

#include <mosquitto.h>
#include <mosquitto_plugin.h>
#include <mosquitto_broker.h>


///////////////////////////////////////////////////////////////////////
// Authentication
//

int mosquitto_auth_unpwd_check(void *user_data, struct mosquitto *client, const char *username, const char *password) {
	const char* address = mosquitto_client_address(client);
	const int protocol = mosquitto_client_protocol(client);

	// Internal connection
	if (address == NULL) {
		return MOSQ_ERR_SUCCESS;
	}

	// Direct connections over MQTT are always allowed,
	// and are used to bootstrap the webserver. Only
	// mp_websockets connections need authentication.
	if (protocol == mp_mqtt) {
		return MOSQ_ERR_SUCCESS;
	}

	// unpwd_check shouldn't even be called if there's no un/pwd?
	if (username == NULL || password == NULL) {
		return MOSQ_ERR_AUTH;
	}

	// special case for unit tests
	if (strcmp(username, "test") == 0 || strcmp(password, "test") == 0) {
		mosquitto_log_printf(MOSQ_LOG_INFO, "mosquitto_auth_unpwm_check(%s, XXX) => test", username);
		return MOSQ_ERR_SUCCESS;
	}

	int rc;
	int rv;
	CURL *ch;

	if ((ch = curl_easy_init()) == NULL) {
		mosquitto_log_printf(MOSQ_LOG_WARNING, "failed to initialize curl (curl_easy_init AUTH): %s", strerror(errno));
		return MOSQ_ERR_AUTH;
	}

	char *escaped_username;
	char *escaped_password;
	char url[256];

	escaped_username = curl_easy_escape(ch, username, 0);
	escaped_password = curl_easy_escape(ch, password, 0);
	snprintf(url, 256, "http://website:6543/queue/%s/admin.json?password=%s", escaped_username, escaped_password);

	curl_easy_setopt(ch, CURLOPT_URL, url);
	if ((rv = curl_easy_perform(ch)) == CURLE_OK) {
		curl_easy_getinfo(ch, CURLINFO_RESPONSE_CODE, &rc);
		rv = rc;
	} else {
		mosquitto_log_printf(MOSQ_LOG_WARNING, "Curl didn't return OK: %s", curl_easy_strerror(rv));
		rv = -1;
	}

	curl_free(escaped_username);
	curl_free(escaped_password);
	curl_easy_cleanup(ch);
	if (rv == -1) {
		return MOSQ_ERR_AUTH;
	}
	mosquitto_log_printf(MOSQ_LOG_INFO, "mosquitto_auth_unpwm_check(%s, XXX) => %d", username, rc);

	return (rc == 200 ? MOSQ_ERR_SUCCESS : MOSQ_ERR_AUTH);
}


///////////////////////////////////////////////////////////////////////
// Authorisation
//

bool starts_with(const char *str, const char *pre)
{
    size_t lenpre = strlen(pre),
           lenstr = strlen(str);
    return lenstr < lenpre ? false : memcmp(pre, str, lenpre) == 0;
}

int mosquitto_auth_acl_check(void *user_data, int access, struct mosquitto *client, const struct mosquitto_acl_msg *msg) {
	const char* address = mosquitto_client_address(client);
	const char* username = mosquitto_client_username(client);
	int protocol = mosquitto_client_protocol(client);
	const char* topic = msg->topic;
	char* access_s = "unknown";

	if (access == MOSQ_ACL_SUBSCRIBE) {
		access_s = "subscribe";
	} else if (access == MOSQ_ACL_READ) {
		access_s = "read";
	} else if (access == MOSQ_ACL_WRITE) {
		access_s = "write";
	}

	if (username == NULL) {
		username = "[null]";
	}
	char my_room[64];
	snprintf(my_room, 64, "karakara/room/%s/", username);

	// Internal connection
	if (address == NULL) {
		// this happens so often, don't even log it
		// mosquitto_log_printf(MOSQ_LOG_DEBUG, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Internal connction OK", address, username, topic, access_s);
		return MOSQ_ERR_SUCCESS;
	}

	// Direct connections over MQTT are always allowed,
	// and are used to bootstrap the webserver. Only
	// mp_websockets connections need authorisation.
	else if (protocol == mp_mqtt) {
		mosquitto_log_printf(MOSQ_LOG_DEBUG, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Raw TCP OK", address, username, topic, access_s);
		return MOSQ_ERR_SUCCESS;
	}

	// Subscribing to everything is fine, doesn't mean
	// the user can _read_ everything
	else if (access == MOSQ_ACL_SUBSCRIBE) {
		mosquitto_log_printf(MOSQ_LOG_DEBUG, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Subscribe OK", address, username, topic, access_s);
		return MOSQ_ERR_SUCCESS;
	}

    // Special cases for unit tests
    else if(starts_with(topic, "test/public/")) {
		mosquitto_log_printf(MOSQ_LOG_DEBUG, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Public test OK", address, username, topic, access_s);
		return MOSQ_ERR_SUCCESS;
	}
    else if(strcmp(username, "test") == 0 && starts_with(topic, "test/private/")) {
		mosquitto_log_printf(MOSQ_LOG_DEBUG, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Private test OK", address, username, topic, access_s);
		return MOSQ_ERR_SUCCESS;
	}

    // Each room can write to its own topics
    else if(starts_with(topic, my_room)) {
		mosquitto_log_printf(MOSQ_LOG_DEBUG, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Write own room OK", address, username, topic, access_s);
		return MOSQ_ERR_SUCCESS;
	}

    // Everybody can read room state broadcasts
    else if(starts_with(topic, "karakara/room/") && access == MOSQ_ACL_READ) {
		mosquitto_log_printf(MOSQ_LOG_DEBUG, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Read any room OK", address, username, topic, access_s);
		return MOSQ_ERR_SUCCESS;
	}

	// Default
	else {
		mosquitto_log_printf(MOSQ_LOG_INFO, "mosquitto_auth_acl_check(%s, %s, %s, %s) => Default ERR", address, username, topic, access_s);
		return MOSQ_ERR_ACL_DENIED;
	}
}


///////////////////////////////////////////////////////////////////////
// Things which aren't relevant to this use-case
//

int mosquitto_auth_plugin_init(void **user_data, struct mosquitto_opt *auth_opts, int auth_opt_count) {
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_auth_plugin_version(void) {
	return MOSQ_AUTH_PLUGIN_VERSION;
}

int mosquitto_auth_plugin_cleanup(void *user_data, struct mosquitto_opt *auth_opts, int auth_opt_count) {
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_auth_security_init(void *user_data, struct mosquitto_opt *auth_opts, int auth_opt_count, bool reload) {
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_auth_security_cleanup(void *user_data, struct mosquitto_opt *auth_opts, int auth_opt_count, bool reload) {
	return MOSQ_ERR_SUCCESS;
}

int mosquitto_auth_psk_key_get(void *user_data, struct mosquitto *client, const char *hint, const char *identity, char *key, int max_key_len) {
	return MOSQ_ERR_AUTH;
}

