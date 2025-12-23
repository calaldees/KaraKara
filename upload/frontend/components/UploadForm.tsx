import { useState, useRef } from "react";
import type { FormEvent } from "react";
import * as tus from 'tus-js-client';
import { useLocalStorage } from "usehooks-ts";

interface UploadProgress {
    filename: string;
    progress: number;
}

const ContactInfoSection = () => {
    const [contact, setContact] = useLocalStorage('karakara_contact_info', '');

    return (
        <section>
            <h3>Your contact info (Required)</h3>
            <p>
                To ask clarifying questions / let you know if there are any
                issues
            </p>
            <input
                type="text"
                name="contact"
                placeholder='eg "MrBob on the BlahCon Discord"'
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                required
            />
        </section>
    );
};

const TrackTitleSection = () => (
    <section>
        <h3>Track Title (Required)</h3>
        <input type="text" name="title" required />
    </section>
);

const ArtistsSection = () => (
    <section>
        <h3>Artist(s)</h3>
        <ul className="check cols3">
            <li>
                <input type="text" name="artist" />
            </li>
            <li>
                <input type="text" name="artist" />
            </li>
            <li>
                <input type="text" name="artist" />
            </li>
            <li>
                <input type="text" name="artist" />
            </li>
            <li>
                <input type="text" name="artist" />
            </li>
            <li>
                <input type="text" name="artist" />
            </li>
        </ul>
    </section>
);

const CategorySection = () => (
    <section>
        <h3>Category</h3>
        <ul className="check cols3">
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="anime"
                    />{" "}
                    Anime
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="cartoon"
                    />{" "}
                    Cartoon
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="game"
                    />{" "}
                    Game
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="jpop"
                    />{" "}
                    JPop
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="kpop"
                    />{" "}
                    KPop
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="tokusatsu"
                    />{" "}
                    Tokusatsu
                </label>
            </li>
            <li>
                <label>
                    <input type="checkbox" name="category" value="tv" />{" "}
                    TV
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="vocaloid"
                    />{" "}
                    Vocaloid
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="category"
                        value="oddballs"
                    />{" "}
                    Other
                </label>
            </li>
        </ul>
    </section>
);

const FromSection = () => (
    <section>
        <h3>From (Series / Game / Movie name)</h3>
        <input
            type="text"
            name="from"
            placeholder="Original name (eg Boku no Hero Academia)"
        />
        <input
            type="text"
            name="from"
            placeholder="Alt name, if applicable (eg My Hero Academia)"
        />
    </section>
);

const UseSection = () => (
    <section>
        <h3>Use</h3>
        <ul className="check cols3">
            <li>
                <label>
                    <input type="checkbox" name="use" value="opening" />{" "}
                    Opening
                </label>
            </li>
            <li>
                <label>
                    <input type="checkbox" name="use" value="ending" />{" "}
                    Ending
                </label>
            </li>
            <li>
                <label>
                    <input type="checkbox" name="use" value="insert" />{" "}
                    Insert
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="use"
                        value="character"
                    />{" "}
                    Character Song
                </label>
            </li>
            <li>
                <label>
                    <input type="checkbox" name="use" value="doujin" />{" "}
                    Doujin / Fan-Song
                </label>
            </li>
            <li>
                <label>
                    <input type="checkbox" name="use" value="trailer" />{" "}
                    Trailer
                </label>
            </li>
            <li>
                <label>
                    Other: <input type="text" name="use" />
                </label>
            </li>
        </ul>
    </section>
);

const LanguageSection = () => (
    <section>
        <h3>Language</h3>
        <ul className="check cols2">
            <li>
                <label>
                    <input type="checkbox" name="lang" value="en" />{" "}
                    English
                </label>
            </li>
            <li>
                <label>
                    <input type="checkbox" name="lang" value="jp" />{" "}
                    Japanese
                </label>
            </li>
            <li>
                <label>
                    <input type="checkbox" name="lang" value="kr" />{" "}
                    Korean
                </label>
            </li>
            <li>
                <label>
                    Other: <input type="text" name="lang" />
                </label>
            </li>
        </ul>
    </section>
);

const VocalStyleSection = () => (
    <section>
        <h3>Vocal style</h3>
        <ul className="check cols2">
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="vocalstyle"
                        value="male"
                    />{" "}
                    Male
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="vocalstyle"
                        value="female"
                    />{" "}
                    Female
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="vocalstyle"
                        value="duet"
                    />{" "}
                    Duet
                </label>
            </li>
            <li>
                <label>
                    <input
                        type="checkbox"
                        name="vocalstyle"
                        value="group"
                    />{" "}
                    Group
                </label>
            </li>
            <li>
                <label>
                    Other: <input type="text" name="vocalstyle" />
                    <br />
                    &nbsp;
                </label>
            </li>
        </ul>
    </section>
);

const VocalTrackSection = () => (
    <section>
        <h3>Vocal or Instrumental</h3>
        <p>
            (Note that it's considerably easier to add an instrumental
            if we already have the vocal version in our database)
        </p>
        <ul className="check">
            <li>
                <label>
                    <input type="radio" name="vocaltrack" value="on" />{" "}
                    Vocal
                </label>
            </li>
            <li>
                <label>
                    <input type="radio" name="vocaltrack" value="off" />{" "}
                    Instrumental
                </label>
            </li>
        </ul>
    </section>
);

const ReleaseDateSection = () => (
    <section>
        <label>
            <h3>Release date</h3>
            <input type="date" name="date" />
        </label>
    </section>
);

const VideoFileSection = () => (
    <section>
        <h3>Video (or Audio) File</h3>
        <ul>
            <li>Without baked-in subtitles or watermarks</li>
            <li>
                DVD / Bluray "special features" often include creditless
                OPs/EDs - these are ideal
            </li>
            <li>
                If the video is just a static image, then uploading
                audio file + image is preferred over uploading a video
                file
            </li>
            <li>
                Pretty much any video format is fine as input; it'll all
                get re-encoded to optimised files for iphones / androids
                / projectors
            </li>
            <li>
                If the video doesn't have clean audio (eg characters are
                talking over the top of an insert song), we'd want a
                different copy of the audio (eg from a soundtrack album)
                which can be spliced together
            </li>
        </ul>
        <input multiple type="file" accept="video/*, audio/*" />
    </section>
);

const ImageSection = () => (
    <section>
        <h3>Image</h3>
        <ul>
            <li>
                Required if you're uploading an audio file, optional
                otherwise
            </li>
            <li>
                If the video has a particularly good moment to use as a
                thumbnail, take a screenshot and upload that (otherwise
                the system will pick a random moment from the video to
                use as a thumbnail)
            </li>
        </ul>
        <input type="file" accept="image/*" />
    </section>
);

const SubtitlesSection = () => (
    <section>
        <h3>Subtitles</h3>
        <ul>
            <li>
                The end goal is to get a .srt subtitle file with
                accurate timings; if you have this, it'll save a lot of
                work :) Personally I'm making these with Aegisub but
                anything which outputs SRT files should work.
            </li>
            <li>
                Don't do anything fancy - no formatting, no mid-line
                timings, no "[instrumental break]" markers, no preview
                of the next line &mdash; the input .srt file should{" "}
                <em>only</em> contain the timings for the lyrics at the
                moment that they are being sung, and the system will
                take care of the rest automatically
            </li>
            <li>
                Western alphabet (eg, english or romaji) required, other
                alphabets (eg hiragana or hangul) can optionally be
                added as extras
            </li>
        </ul>
        <input type="file" id="textFiles" multiple accept=".srt" />
    </section>
);

const ContributorSection = () => (
    <section>
        <label>
            <h3>Contributor(s)</h3>
            <p>
                If you've done the subtitling / editing work yourself,
                what name would you like to be credited as?
            </p>
            <input type="text" name="contributor" />
        </label>
    </section>
);

const LinksInfoSection = () => (
    <section>
        <h3>Links / any other info</h3>
        <ul>
            <li>
                If you don't have a subtitle file, a link to a website
                with the lyrics is helpful
            </li>
            <li>
                If you don't have a video file, specifying the season /
                episode number can help to track one down
            </li>
            <li>
                Youtube links are helpful to make sure we've got the
                right version of the right song, but rarely work well as
                sources (frequent watermarks, extra "like and subscribe
                for more!!!" clips tacked onto the beginning or end,
                weird cropping, inconsistent volumes...)
            </li>
        </ul>
        <textarea name="info" rows={4}></textarea>
    </section>
);

export const UploadForm = () => {
    const [hasFiles, setHasFiles] = useState(false);
    const [uploads, setUploads] = useState<UploadProgress[]>([]);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const formRef = useRef<HTMLFormElement>(null);

    const updateButtonLabel = () => {
        if (!formRef.current) return;
        const fileInputs = formRef.current.querySelectorAll('input[type="file"]');
        let foundFiles = false;
        fileInputs.forEach((input) => {
            const fileInput = input as HTMLInputElement;
            if (fileInput.files && fileInput.files.length > 0) {
                foundFiles = true;
            }
        });
        setHasFiles(foundFiles);
    };

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (isSubmitting) return;

        setIsSubmitting(true);
        setUploads([]);

        const form = formRef.current;
        if (!form) return;

        try {
            // 1. Collect metadata (all non-file inputs)
            const formData = new FormData(form);
            const metadata: Record<string, string[]> = {};

            for (const [key, value] of formData.entries()) {
                const el = form.querySelector(`[name="${key}"]`) as HTMLInputElement;
                if (!el || el.type !== "file") {
                    if (metadata[key]) {
                        metadata[key].push(value as string);
                    } else {
                        metadata[key] = [value as string];
                    }
                }
            }

            // 2. Collect all files from any input[type="file"]
            const fileInputs = form.querySelectorAll('input[type="file"]');
            const files: File[] = [];
            fileInputs.forEach((input) => {
                const fileInput = input as HTMLInputElement;
                if (fileInput.files) {
                    Array.from(fileInput.files).forEach((f) => files.push(f));
                }
            });

            let url: string;
            let body: any;

            // 3. If there are files, do a file upload for /submit
            if (files.length > 0) {
                const res = await fetch("./session", { method: "POST" });
                const data = await res.json();
                const sessionId = data.session_id;

                // Initialize upload progress state
                setUploads(files.map(file => ({ filename: file.name, progress: 0 })));

                const uploadPromises = files.map((file, index) => {
                    return new Promise<void>((resolve, reject) => {
                        const upload = new tus.Upload(file, {
                            endpoint: "./files/",
                            metadata: {
                                filename: file.name,
                                session_id: sessionId,
                            },
                            parallelUploads: 1,
                            chunkSize: 5 * 1024 * 1024, // 5MB
                            storeFingerprintForResuming: true,
                            onProgress(bytesSent: number, bytesTotal: number) {
                                console.log(`${file.name}: ${bytesSent}/${bytesTotal}`);
                                const progress = Math.round((bytesSent / bytesTotal) * 100);
                                setUploads(prev => {
                                    const newUploads = [...prev];
                                    newUploads[index] = { filename: file.name, progress };
                                    return newUploads;
                                });
                            },
                            onError(err: Error) {
                                console.error("Upload failed:", err);
                                reject(err);
                            },
                            onSuccess() {
                                console.log(`${file.name} upload complete`);
                                setUploads(prev => {
                                    const newUploads = [...prev];
                                    newUploads[index] = { filename: file.name, progress: 100 };
                                    return newUploads;
                                });
                                resolve();
                            },
                        });
                        upload.start();
                    });
                });

                await Promise.all(uploadPromises);

                url = "./submit";
                body = { session_id: sessionId, tags: metadata };
            }
            // 4. If no files, just send metadata to /request
            else {
                url = "./request";
                body = { tags: metadata };
            }

            const finalizeRes = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const finalizeData = await finalizeRes.json();

            if (finalizeData.ok) {
                alert("Thank you, an admin should take a look at it soon <3");
                form.reset();
                setHasFiles(false);
            } else {
                throw new Error(finalizeData.error || "Unknown error");
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : String(err);
            alert(
                "There was an error processing your submission: " +
                    errorMessage +
                    " - maybe refresh the page and try again? D:"
            );
        } finally {
            setIsSubmitting(false);
            setUploads([]);
        }
    };

    return (
        <form id="upload-form" ref={formRef} onChange={updateButtonLabel} onSubmit={handleSubmit}>
            <ContactInfoSection />
            <TrackTitleSection />
            <ArtistsSection />
            <CategorySection />
            <FromSection />
            <UseSection />
            <LanguageSection />
            <VocalStyleSection />
            <VocalTrackSection />
            <ReleaseDateSection />
            <VideoFileSection />
            <ImageSection />
            <SubtitlesSection />
            <ContributorSection />
            <LinksInfoSection />

            {uploads.length > 0 && (
                <section id="uploads">
                    {uploads.map((upload, index) => (
                        <div key={index} className="file-row">
                            <strong>{upload.filename}</strong>
                            <progress className="bar" value={upload.progress} max="100" />
                        </div>
                    ))}
                </section>
            )}

            <button type="submit" disabled={isSubmitting}>
                {isSubmitting
                    ? "Processing..."
                    : hasFiles
                        ? "Start Upload"
                        : "Send Suggestion"
                }
            </button>
        </form>
    );
};
