import { useEffect, useState } from "react";

import mqtt_client from "u8-mqtt/esm/web/index.js";

export function useMqtt(url: string) {
    const [client, setClient] = useState(null);

    useEffect(() => {
        let my_mqtt = mqtt_client().with_websock(url).with_autoreconnect();

        my_mqtt.connect().then(() => {
            setClient(my_mqtt);
        });

        return () => {
            my_mqtt.disconnect();
            setClient(null);
        };
    }, [url]);

    return { client };
}

export function useMqttSubscription(
    client: any,
    topic: string,
    callback: (msg: any) => void,
) {
    useEffect(() => {
        if (client) {
            client.subscribe_topic(topic, (pkt: any, params: any, ctx: any) => {
                console.groupCollapsed(`mqtt_msg(${topic})`);
                console.log(pkt.json());
                console.groupEnd();
                callback(pkt.json());
            });

            return () => {
                client.unsubscribe(topic);
            };
        }
    }, [client, topic]);
}
