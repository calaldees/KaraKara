import { useTexture } from "@react-three/drei";
import { Canvas, useFrame, useLoader, useThree } from "@react-three/fiber";
import { useContext, useMemo, useRef } from "react";
import * as THREE from "three";
import { Group, TextureLoader } from "three";
import { useMediaQuery } from "usehooks-ts";

import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import type { Track } from "@/types";
import { attachment_path } from "@/utils";
import { useMemoArr } from "@/hooks/memo";

import world from "@/static/world.svg";
import "./globe.scss";

function StatsTable({ tracks }: { tracks: Record<string, Track> }) {
    // computing stats only takes ~10ms, but we don't want that to happen
    // in the middle of rendering the globe
    const stats = useMemo(() => {
        const ts = Object.values(tracks);
        return {
            tracks: ts.length,
            artists: new Set(ts.map((t) => t.tags.artist?.[0])).size,
            shows: new Set(ts.map((t) => t.tags.from?.[0])).size,
            hours: Math.floor(
                ts.map((t) => t.duration).reduce((sum, n) => sum + n, 0) /
                    60 /
                    60,
            ),
        };
    }, [tracks]);
    return (
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
    );
}

function getNiceTracks(tracks: Record<string, Track>, n: number) {
    return Object.values(tracks)
        .filter((track) => track.tags["subs"]?.includes("soft"))
        .filter((track) => track.tags["aspect_ratio"]?.includes("16:9"))
        .filter((track) => track.tags["source_type"]?.includes("image"))
        .filter((track) => track.tags["vocaltrack"]?.includes("on"))
        .slice(0, n);
}

function PlaneMaterial({ thumb }: { thumb: string }) {
    const texture = useTexture(thumb);
    return (
        <meshBasicMaterial
            map={texture}
            toneMapped={false}
            side={THREE.DoubleSide}
        />
    );
}

function MyScene() {
    const { tracks } = useContext(ServerContext);
    const widescreen = useMediaQuery("(min-aspect-ratio: 16/10)");

    const globe = useRef<Group>(null);
    const text1 = useRef<Group>(null);
    const text2 = useRef<Group>(null);
    const colorMap = useLoader(TextureLoader, world) as THREE.Texture;

    const thumbs = useMemoArr(() => {
        return getNiceTracks(tracks, 20).map((track) =>
            attachment_path(track.attachments.image[0]),
        );
    }, [tracks]);

    useThree((state) => {
        // these debug functions can randomly take ~100ms
        // on raspberry pi (less on more powerful machines),
        // which causes a noticeable stutter in the animation
        state.gl.getContext().getProgramInfoLog = () => "";
        state.gl.getContext().getShaderInfoLog = () => "";
    });
    useFrame((state, _delta) => {
        const cam = state.camera as THREE.PerspectiveCamera;
        cam.fov = widescreen ? 50 : 65;
        cam.updateProjectionMatrix();

        const t = state.clock.getElapsedTime();
        if (globe.current) globe.current.rotation.y = t / 8;
        if (text1.current)
            text1.current.lookAt(0, Math.sin(1.5 * t), Math.sin(t));
        if (text2.current)
            text2.current.lookAt(0, -Math.sin(1.5 * t), Math.sin(t));
    });

    return (
        <>
            <ambientLight intensity={0.3} />
            <directionalLight
                color="#29EDF2"
                position={[-4, 2, 5]}
                intensity={3}
            />
            <group position={[3, -0.25, 0]} rotation={[0, 0, -0.15]}>
                <group ref={globe}>
                    <mesh>
                        <sphereGeometry args={[2.99, 20, 20]} />
                        <meshStandardMaterial
                            args={[{ flatShading: false }]}
                            color={"#074D5E"}
                            metalness={0.5}
                            roughness={0.5}
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
                    {thumbs.map((thumb, n) => (
                        <group key={n} rotation={[0, -0.314 * n, 0]}>
                            <mesh position={[0, 0, 3.5]}>
                                <planeGeometry args={[1, 9 / 16]} />
                                <PlaneMaterial thumb={thumb} />
                            </mesh>
                        </group>
                    ))}
                </group>
            </group>
        </>
    );
}

export default function Globe() {
    const { settings } = useContext(RoomContext);
    const { tracks } = useContext(ServerContext);
    return (
        <div id={"splash"}>
            <Canvas>
                <MyScene />
            </Canvas>
            <div className="html3d">
                <h1>{settings["title"]}</h1>
                <h2>
                    <StatsTable tracks={tracks} />
                </h2>
            </div>
        </div>
    );
}
