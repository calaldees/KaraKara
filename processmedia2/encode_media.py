import os.path
import tempfile

from libs.misc import postmortem, hashfile, freeze, first, file_ext
from libs.file import FolderStructure

from processmedia_libs import add_default_argparse_args, EXTS
from processmedia_libs import external_tools
from processmedia_libs.meta_manager import MetaManager, FileItemWrapper
from processmedia_libs.processed_files_manager import ProcessedFilesManager, gen_string_hash
from processmedia_libs import subtitle_processor


import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'



def main(**kwargs):
    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()

    encoder = Encoder(meta, **kwargs)

    # In the full system, encode will probably be driven from a rabitmq endpoint.
    # For testing locally we are monitoring the 'pendings_actions' list
    for name in (
        #'Cuticle Tantei Inaba - OP - Haruka Nichijou no Naka de',
        #'Gosick - ED2 - Unity (full length)',
        #'Ranma Half OP1 - Jajauma ni Sasenaide',
        #'Tamako Market - OP - Dramatic Market Ride',
        #'Fullmetal Alchemist - OP1 - Melissa',  # Exhibits high bitrate pausing at end
        'Samurai Champloo - OP - Battlecry',  # Missing title sub with newline
        'KAT-TUN Your side [Instrumental]',

        #m.name for m in meta.meta.values() #if m.pending_actions
    ):
        encoder.encode(name)


class Encoder(object):
    """
        consume for
         - update tags
         - extract lyrics
         - encode media
        ENCODE (queue consumer)
            listen to queue
            -Encode-
            Update meta destination hashs
            -CLEANUP-
            prune unneeded files from destination
            trigger importer
    choose encode type
     - video
     - video + sub
     - video + audio
     - image + sub + audio
    input hashs cmp output hash
    encode hi-res
     - normalize audio
     - normalize subtitles
       - srt to ssa
       - rewrite playres
       - remove dupes
       - add next line
    preview encode
    gen thumbnail images
    extract subs
    """

    def __init__(self, meta_manager=None, path_meta=None, path_processed=None, path_source=None, **kwargs):
        self.meta = meta_manager or MetaManager(path_meta)
        self.fileitem_wrapper = FileItemWrapper(path_source)
        self.processed_files_manager = ProcessedFilesManager(path_processed)

    def _get_meta(self, name):
        self.meta.load(name)
        return self.meta.get(name)

    def encode(self, name):
        """
        Todo: save the meta on return ... maybe use a context manager
        """
        log.info('Encode: %s', name)
        self.meta.load(name)
        m = self.meta.get(name)
        self._encode_primary_video_from_meta(m)

        if not m.source_hash:
            log.warn('No source_hash to extract additional media %s', name)
            return

        if all((
                self._encode_preview_video_from_meta(m),
                self._encode_images_from_meta(m),
                self._process_tags_from_meta(m),
        )):
            self.meta.save(name)

    def _encode_primary_video_from_meta(self, m):
        # 1.) Calculate starting files 'source_hash' and allocate a master 'target_file'
        source_files = self.fileitem_wrapper.wrap_scan_data(m)
        m.source_hash = gen_string_hash(f['hash'] for f in source_files.values() if f)  # Derive the source hash from the child component hashs
        target_file = self.processed_files_manager.get_processed_file(m.source_hash, 'video')

        # 2.) Assertain if encoding is actually needed by hashing sources and comparing input and output hashs
        if target_file.exists:
            log.info('Processed Destination was created with the same input sources - no encoding required')
            return True

        m.source_details.update({k:v for k, v in external_tools.probe_media(source_files['image'].get('absolute')).items() if k in ('width', 'height')})
        m.source_details.update({k:v for k, v in external_tools.probe_media(source_files['audio'].get('absolute')).items() if k in ('duration',)})
        m.source_details.update(external_tools.probe_media(source_files['video'].get('absolute')))

        with tempfile.TemporaryDirectory() as tempdir:
            # 3.) Convert souce formats into appropriate formats for video encoding

            # 3.a) Convert Image to Video
            if source_files['image'] and not source_files['video']:
                image_video_path = os.path.join(tempdir, 'image.mp4')
                external_tools.encode_image_to_video(
                    source=source_files['image']['absolute'],
                    destination=image_video_path,
                    **m.source_details
                )
                source_files['video']['absolute'] = image_video_path

            # 3.b) Normalize subtile files - Create our own managed ssa/srt
            if source_files['sub']:
                # Parse subtitles
                subtitles = subtitle_processor.parse_subtitles(filename=source_files['sub']['absolute'])
                if not subtitles:
                    log.error('Subtitle file explicity given, but was unable to parse any subtitles from it. There may be an issue with parsing')
                    return False

                # Output srt
                temp_srt_file = os.path.join(tempdir, 'subs.srt')
                with open(temp_srt_file, 'w', encoding='utf-8') as subfile:
                    subfile.write(
                        subtitle_processor.create_srt(subtitles)
                    )
                target_srt_file = self.processed_files_manager.get_processed_file(m.source_hash, 'srt')
                target_srt_file.move(temp_srt_file)

                # Output ssa
                temp_ssa_file = os.path.join(tempdir, 'subs.ssa')
                with open(temp_ssa_file, 'w', encoding='utf-8') as subfile:
                    subfile.write(
                        subtitle_processor.create_ssa(subtitles, width=m.source_details['width'], height=m.source_details['height'])
                    )
                source_files['sub']['absolute'] = temp_ssa_file  # It is safe to set this key as it will never be persisted in the meta

            # 4.) Encode
            encode_steps = (
                # 4.a) Render video with subtitles (without audio)
                lambda: external_tools.encode_video(
                    source=source_files['video'].get('absolute'),
                    sub=source_files['sub'].get('absolute'),
                    destination=os.path.join(tempdir, 'video.mp4'),
                ),

                # 4.b) Render audio and normalize
                lambda: external_tools.encode_audio(
                    source=source_files['audio'].get('absolute') or source_files['video'].get('absolute'),
                    destination=os.path.join(tempdir, 'audio.wav'),
                ),

                # 4.c) Mux Video and Audio
                lambda: external_tools.mux(
                    video=os.path.join(tempdir, 'video.mp4'),
                    audio=os.path.join(tempdir, 'audio.wav'),
                    destination=os.path.join(tempdir, 'mux.mp4'),
                )
            )
            for encode_step in encode_steps:
                encode_success, cmd_result = encode_step()
                if not encode_success:
                    import pdb ; pdb.set_trace()
                    return False

            # 5.) Move the newly encoded file to the target path
            target_file.move(os.path.join(tempdir, 'mux.mp4'))

        return True

    def _encode_preview_video_from_meta(self, m):
        source_file = self.processed_files_manager.get_processed_file(m.source_hash, 'video')
        target_file = self.processed_files_manager.get_processed_file(m.source_hash, 'preview')

        if not source_file.exists:
            log.warn('No source video to encode preview from')
            return False

        if target_file.exists:
            log.info('Processed preview was created with the same input sources - no encoding required')
            return True

        with tempfile.TemporaryDirectory() as tempdir:
            preview_file = os.path.join(tempdir, 'preview.mp4')
            encode_success, cmd_result = external_tools.encode_preview_video(
                source=source_file.absolute,
                destination=preview_file,
            )
            if not encode_success:
                import pdb ; pdb.set_trace()
                return False
            target_file.move(preview_file)

        return True


    def _encode_images_from_meta(self, m, num_images=ProcessedFilesManager.DEFAULT_NUMBER_OF_IMAGES):
        source_file_absolute = self.fileitem_wrapper.wrap_scan_data(m)['video'].get('absolute')
        if not source_file_absolute:  # If no video source, attempt to degrade to single image input
            source_file_absolute = self.fileitem_wrapper.wrap_scan_data(m)['image'].get('absolute')

        target_files = tuple(
            self.processed_files_manager.get_processed_file(m.source_hash, 'image', index)
            for index in range(num_images)
        )
        if all(target_file.exists for target_file in target_files):
            log.info('Processed Destination was created with the same input sources - no thumbnail gen required')
            return True

        if file_ext(source_file_absolute).ext in EXTS['image']:
            # If input is a single image, we use it as an imput video and take
            # a frame 4 times from frame zero.
            # This feels inefficent, but we need 4 images for the import check.
            # Variable numbers of images would need more data in the meta
            times = (0, ) * num_images
        else:
            video_duration = m.source_details.get('duration')
            if not video_duration:
                log.warn('Unable to assertain video duration; unable to extact images')
                return False
            times = (float("%.3f" % (video_duration * offset)) for offset in (x/(num_images+1) for x in range(1, num_images+1)))

        with tempfile.TemporaryDirectory() as tempdir:
            for index, time in enumerate(times):
                image_file = os.path.join(tempdir, '{}.jpg'.format(index))
                encode_succes, cmd_result = external_tools.extract_image(source_file_absolute, image_file, time)
                if not encode_succes:
                    import pdb ; pdb.set_trace()
                    return False
                target_files[index].move(image_file)

        return True


    def _process_tags_from_meta(self, m):
        """
        No processing ... this is just a copy
        """
        source_file = self.fileitem_wrapper.wrap_scan_data(m).get('tag', {}).get('absolute')
        target_file = self.processed_files_manager.get_processed_file(m.source_hash, 'tags')

        if not os.path.exists(source_file):
            log.warn('Source file tags does not exists? wtf! %s', source_file)
            return False

        target_file.copy(source_file)

        return target_file.exists


# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 encoder
        """,
        epilog="""
        """
    )

    add_default_argparse_args(parser)

    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(main, **args)
