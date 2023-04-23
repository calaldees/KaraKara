import { Suspense, useContext, useMemo, useRef } from "react";
import { attachment_path } from "../utils";
import { EventInfo, JoinInfo } from "./_common";
import { RoomContext } from "../providers/room";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import { Html, useVideoTexture, useTexture } from '@react-three/drei'
import { Group, TextureLoader } from "three";
import * as THREE from "three";
import world from '../static/world.svg';
import { useMediaQuery } from "usehooks-ts";

///////////////////////////////////////////////////////////////////////
// Common

export function TitleScreen() {
    const { settings } = useContext(RoomContext);
    let splash = null;
    switch (settings['splash']) {
        case "globe":
        default:
            splash = <Globe />;
            break;
        case "waterfall":
            splash = <Waterfall />;
            break;
    }

    return (
        <section key="title" className={"screen_title"}>
            {splash}
            <JoinInfo />
            <EventInfo />
        </section>
    );
}

function StatsTable({ tracks }: { tracks: Record<string, Track> }) {
    const ts = Object.values(tracks);
    const stats = {
        tracks: ts.length,
        lines: ts.map((t) => t.lyrics.length).reduce((sum, n) => sum + n, 0),
        shows: new Set(ts.map((t) => t.tags.from?.[0])).size,
        hours: Math.floor(
            ts.map((t) => t.duration).reduce((sum, n) => sum + n, 0) / 60 / 60,
        ),
    };
    return (
        <h2>
            <table>
                <tbody>
                    {Object.entries(stats).map(([key, value]) => (
                        <tr key={key}>
                            <th>
                                <strong>{value}</strong>
                            </th>
                            <td>{key}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </h2>
    );
}

function getNiceTracks(tracks: Record<string, Track>, n: number) {
    const good_tracks = [
        "AKB0048_ED2_Niji_no_Ressha",
        "07_Ghost_OP1_Aka_no_Kakera",
        "Ah_My_Goddess_TV_ED1_Negai",
        "Jojo_s_Bizarre_Adventure_Stone_Ocean_OP_Stone_Ocean",
        "Gekiganger_3_OP_Seigi_no_Robot_Gekiganger_3",
        "Secret_Madonna_Japanese_version_",
        "Haikyuu_Second_Season_OP1_I_m_a_Believer",
        "Working_OP2_Coolish_Walk",
        "Sailor_Moon_ED2_Princess_Moon",
    ]
        .map((t) => tracks[t])
        .filter((t) => t);
    const first_tracks = Object.values(tracks)
        // ignore instrumental tracks, because instrumentals
        // tend to have hard-subs, which makes ugly thumbnails
        .filter((track) => track.tags.vocaltrack?.[0] !== "off")
        .slice(0, n);
    return [...good_tracks, ...first_tracks].slice(0, n);
}

///////////////////////////////////////////////////////////////////////
// Waterfall

function Waterfall() {
    const { settings } = useContext(RoomContext);
    const { root } = useContext(ClientContext);
    const { tracks } = useContext(ServerContext);
    const items = useMemo(() => {
        return getNiceTracks(tracks, 25).map((track, n, arr) => ({
            src: attachment_path(root, track.attachments.image[0]),
            style: {
                animationDelay: ((n % 5) + Math.random()) * 2 + "s",
                animationDuration: 5 + Math.random() * 5 + "s",
                left: (n / arr.length) * 90 + "vw",
            },
        }));
    }, [tracks, root]);
    return (
        <>
            <div id={"splash"}>
                {items.map(({ src, style }, n) => (
                    <img key={n} alt="" src={src} style={style} />
                ))}
            </div>
            <h1>{settings["title"]}</h1>
        </>
    );
}

///////////////////////////////////////////////////////////////////////
// Globe

function VideoMaterial({ url }: { url: string }) {
    const texture = useVideoTexture(url)
    return <meshBasicMaterial map={texture} toneMapped={false} />
}

function FallbackMaterial({ url }: { url: string }) {
    const texture = useTexture(url)
    return <meshBasicMaterial map={texture} toneMapped={false} side={THREE.DoubleSide} />
}

function PlaneMaterial({ thumb, vid }: { thumb: string, vid: string }) {
    const videos = false;
    return videos ?
        <Suspense fallback={<FallbackMaterial url={thumb} />}>
            <VideoMaterial url={vid} />
        </Suspense> :
        <FallbackMaterial url={thumb} />;
}

function MyScene() {
    const { root } = useContext(ClientContext);
    const { settings } = useContext(RoomContext);
    const { tracks } = useContext(ServerContext);
    const widescreen = useMediaQuery(
        "(min-aspect-ratio: 16/10)",
    );

    const globe = useRef<Group>(null);
    const text1 = useRef<Group>(null);
    const text2 = useRef<Group>(null);
    const colorMap = useLoader(TextureLoader, world) as THREE.Texture;

    const thumbs = useMemo(() => {
        return getNiceTracks(tracks, 20).map((track) => [
            attachment_path(root, track.attachments.image[1]),
            attachment_path(root, track.attachments.preview[0])
        ]);
    }, [tracks])

    useFrame(({ camera, clock }) => {
        (camera as THREE.PerspectiveCamera).fov = widescreen ? 50 : 65;
        const t = clock.getElapsedTime()
        globe.current && (globe.current.rotation.y = t / 8)
        text1.current && text1.current.lookAt(0, Math.sin(1.5 * t), Math.sin(t));
        text2.current && text2.current.lookAt(0, -Math.sin(1.5 * t), Math.sin(t));
        //console.log(a) // the value will be 0 at scene initialization and grow each frame
    })

    return <>
        <ambientLight intensity={0.1} />
        <directionalLight color="#29EDF2" position={[-4, 2, 5]} />
        <group position={[3, -0.25, 0]} rotation={[0, 0, -0.15]}>
            <group ref={globe}>
                <mesh>
                    <sphereGeometry args={[2.99, 20, 20]} />
                    <meshStandardMaterial
                        args={[{ flatShading: false }]}
                        color={"#074D5E"}
                        metalness={.5}
                        roughness={.5}
                    />
                </mesh>
                <mesh>
                    <sphereGeometry args={[3, 20, 20]} />
                    <meshStandardMaterial
                        args={[{ flatShading: false }]}
                        map={colorMap}
                        color={"#29EDF2"}
                        transparent={true}
                    />
                </mesh>
                {thumbs.map(([thumb, vid], n) =>
                    <group key={n} rotation={[0, -0.314 * n, 0]}>
                        <mesh position={[0, 0, 3.5]}>
                            <planeGeometry args={[1, 0.75]} />
                            <PlaneMaterial thumb={thumb} vid={vid} />
                        </mesh>
                    </group>
                )}
            </group>
        </group>
        <group ref={text1} position={[-4, 2.5, -5]} onUpdate={self => self.lookAt(0, 0, 0)}>
            <Html transform>
                <h1>{settings["title"]}</h1>
            </Html>
        </group>
        <group ref={text2} position={[-4, -1.5, -5]}>
            <Html transform><StatsTable tracks={tracks} /></Html>
        </group>
    </>
}

function Globe() {
    return (
        <div id={"splash"}>
            <Canvas>
                <MyScene />
            </Canvas>
        </div>
    );
}
