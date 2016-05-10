import os.path
import tempfile
import random

from clint.textui.progress import bar as progress_bar

from libs.misc import postmortem, hashfile, freeze, first, file_ext
from libs.file import FolderStructure

from processmedia_libs import add_default_argparse_args, parse_args, EXTS, PENDING_ACTION
from processmedia_libs import external_tools
from processmedia_libs.meta_manager import MetaManager
from processmedia_libs.source_files_manager import SourceFilesManager
from processmedia_libs.processed_files_manager import ProcessedFilesManager, gen_string_hash
from processmedia_libs import subtitle_processor


import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'

def shuffle(iterable):
    rendered_list = list(iterable)
    random.shuffle(rendered_list)
    return rendered_list
DEFAULT_ORDER_FUNC = 'sorted'
PROCESS_ORDER_FUNCS = {
    'sorted': sorted,
    'random': shuffle,
    'none': lambda x: x,
}

def encode_media(process_order_function=PROCESS_ORDER_FUNCS[DEFAULT_ORDER_FUNC] , **kwargs):
    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()

    encoder = Encoder(meta, **kwargs)

    # In the full system, encode will probably be driven from a rabitmq endpoint.
    # For testing locally we are monitoring the 'pendings_actions' list
    for name in progress_bar(process_order_function(
            m.name for m in meta.meta.values()
            if PENDING_ACTION['encode'] in m.pending_actions or not m.source_hash
        #(
            #'Ikimonogakari - Sakura', # Takes 2 hours to encode
            #'Get Backers - ED2 - Namida no Hurricane', # It's just fucked
            #'Nana (anime) - OP - Rose',  # SSA's have malformed unicode characters
            #'Frozen Japanise (find real name)'  # took too long to process
            #'Lunar Silver Star Story - OP - Wings (Japanese Version)',
            #'Evangleion ED - Fly Me To The Moon',  # Odd dimensions and needs to be normalised
        #    'AKB0048 Next Stage - ED1 - Kono Namida wo Kimi ni Sasagu',
        #'Cuticle Tantei Inaba - OP - Haruka Nichijou no Naka de',
        #'Gosick - ED2 - Unity (full length)',
        #'Ranma Half OP1 - Jajauma ni Sasenaide',
        #'Tamako Market - OP - Dramatic Market Ride',
        #'Fullmetal Alchemist - OP1 - Melissa',  # Exhibits high bitrate pausing at end
        #'Samurai Champloo - OP - Battlecry',  # Missing title sub with newline
        #'KAT-TUN Your side [Instrumental]',
        #)
    )):
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
        self.source_files_manager = SourceFilesManager(path_source)
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

        def encode_steps(m):
            source_files = self.source_files_manager.get_source_files(m)
            yield self._update_source_hash(m, source_files)
            #target_files = 
            yield self._encode_primary_video_from_meta(m, source_files)
            yield self._encode_srt_from_meta(m, source_files)
            yield self._encode_preview_video_from_meta(m)
            yield self._encode_images_from_meta(m, source_files)
            yield self._process_tags_from_meta(m, source_files)
        if all(encode_steps(m)):
            try:
                m.pending_actions.remove(PENDING_ACTION['encode'])
            except ValueError:
                pass
            self.meta.save(name)

    def _update_source_hash(self, m, source_files=None):
        source_files = source_files or self.source_files_manager.get_source_files(m)
        m.source_hash = gen_string_hash(f['hash'] for f in source_files.values() if f)  # Derive the source hash from the child component hashs
        return m.source_hash

    def _update_source_details(self, m, source_files=None):
        source_files = source_files or self.source_files_manager.get_source_files(m)
        source_details = {}
        source_details.update({k:v for k, v in external_tools.probe_media(source_files['image'].get('absolute')).items() if k in ('width', 'height')})
        source_details.update({k:v for k, v in external_tools.probe_media(source_files['audio'].get('absolute')).items() if k in ('duration',)})
        source_details.update(external_tools.probe_media(source_files['video'].get('absolute')))
        m.source_details.update(source_details)

    def _encode_primary_video_from_meta(self, m, source_files):
        target_file = self.processed_files_manager.get_processed_file(m.source_hash, 'video')
        if target_file.exists:
            log.debug('Processed Destination was created with the same input sources - no encoding required')
            return True

        # 1.) Probe media to persist source details in meta
        self._update_source_details(m, source_files)

        if not m.source_details.get('duration'):
            log.error('Unable to identify source duration. Maybe the source file is damaged? {}'.format(m.name))
            return False

        with tempfile.TemporaryDirectory() as tempdir:
            # 3.) Convert souce formats into appropriate formats for video encoding

            absolute_video_to_encode = source_files['video'].get('absolute')

            # 3.a) Convert Image to Video
            if source_files['image'] and not absolute_video_to_encode:
                absolute_video_to_encode = os.path.join(tempdir, 'image.mp4')
                external_tools.encode_image_to_video(
                    source=source_files['image']['absolute'],
                    destination=absolute_video_to_encode,
                    **m.source_details
                )

            if not absolute_video_to_encode:
                log.error('Unable to encode as no video was provided {}'.format(absolute_video_to_encode))
                return False
            if not os.path.exists(absolute_video_to_encode):
                log.error('Video to encode does not exist {}'.format(absolute_video_to_encode))
                return False

            # 3.b) Read + normalize subtitle file
            absolute_ssa_to_encode = None
            if source_files['sub']:
                # Parse input subtitles
                subtitles = subtitle_processor.parse_subtitles(filename=source_files['sub']['absolute'])
                if not subtitles:
                    log.error(
                        'Subtitle file explicity given, but was unable to parse any subtitles from it. '
                        'There may be an issue with parsing. '
                        'A Common cause is SSA files that have subtitles aligned at top are ignored. '
                        '{}'.format(source_files['sub']['absolute'])
                    )
                    return False

                # Output styled subtiles as SSA
                absolute_ssa_to_encode = os.path.join(tempdir, 'subs.ssa')
                with open(absolute_ssa_to_encode, 'w', encoding='utf-8') as subfile:
                    subfile.write(
                        subtitle_processor.create_ssa(subtitles, width=m.source_details['width'], height=m.source_details['height'])
                    )

            # 4.) Encode
            encode_steps = (
                # 4.a) Render audio and normalize
                lambda: external_tools.encode_audio(
                    source=source_files['audio'].get('absolute') or source_files['video'].get('absolute'),
                    destination=os.path.join(tempdir, 'audio.wav'),
                ),

                # 4.b) Render video with subtitles and mux new audio.
                lambda: external_tools.encode_video(
                    video_source=absolute_video_to_encode,
                    audio_source=os.path.join(tempdir, 'audio.wav'),
                    subtitle_source=absolute_ssa_to_encode,
                    destination=os.path.join(tempdir, 'video.mp4'),
                ),
            )
            for encode_step in encode_steps:
                encode_success, cmd_result = encode_step()
                if not encode_success:
                    import pdb ; pdb.set_trace()
                    return False

            # 5.) Move the newly encoded file to the target path
            target_file.move(os.path.join(tempdir, 'video.mp4'))

        return True

    def _encode_srt_from_meta(self, m, source_files):
        """
        Always output an srt (even if it contains no subtitles)
        This is required for the importer to verify the processed fileset is complete
        """
        target_file = self.processed_files_manager.get_processed_file(m.source_hash, 'srt')
        if target_file.exists:
            log.debug('Processed srt exists - no parsing required')
            return True

        subtitles = []
        source_file_absolute = source_files['sub'].get('absolute')
        if not source_file_absolute:
            log.warn('No sub file listed in source set. {}'.format(m.name))
        elif not os.path.exists(source_file_absolute):
            log.warn('The source file to extract subs from does not exist {}'.format(source_file_absolute))
        else:
            subtitles = subtitle_processor.parse_subtitles(filename=source_file_absolute)
            if not subtitles:
                log.warn('No subtiles parsed from sub file {}'.format(source_file_absolute))

        with tempfile.TemporaryDirectory() as tempdir:
            srt_file = os.path.join(tempdir, 'subs.srt')
            with open(srt_file, 'w', encoding='utf-8') as subfile:
                subfile.write(
                    subtitle_processor.create_srt(subtitles)
                )
            target_file.move(srt_file)

        return True

    def _encode_preview_video_from_meta(self, m):
        target_file = self.processed_files_manager.get_processed_file(m.source_hash, 'preview')
        if target_file.exists:
            log.debug('Processed preview was created with the same input sources - no encoding required')
            return True

        source_file = self.processed_files_manager.get_processed_file(m.source_hash, 'video')
        if not source_file.exists:
            log.error('No source video to encode preview from')
            return False

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

    def _encode_images_from_meta(self, m, source_files, num_images=ProcessedFilesManager.DEFAULT_NUMBER_OF_IMAGES):
        target_files = tuple(
            self.processed_files_manager.get_processed_file(m.source_hash, 'image', index)
            for index in range(num_images)
        )
        if all(target_file.exists for target_file in target_files):
            log.debug('Processed Destination was created with the same input sources - no thumbnail gen required')
            return True

        source_file_absolute = source_files['video'].get('absolute')
        if not source_file_absolute:  # If no video source, attempt to degrade to single image input
            source_file_absolute = self.source_files_manager.get_source_files(m)['image'].get('absolute')
        if not source_file_absolute:
            log.warn('No video or image input in meta to extract thumbnail images')
            return False
        if not os.path.exists(source_file_absolute):
            log.error('The source file to extract images from does not exist {}'.format(source_file_absolute))
            return False

        if file_ext(source_file_absolute).ext in EXTS['image']:
            # If input is a single image, we use it as an imput video and take
            # a frame 4 times from frame zero.
            # This feels inefficent, but we need 4 images for the import check.
            # Variable numbers of images would need more data in the meta
            times = (0, ) * num_images
        else:
            video_duration = m.source_details.get('duration')
            if not video_duration:
                self._update_source_details(m)  # Bugfix for being tenatious in aquiring duration
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
                    #import pdb ; pdb.set_trace()
                    log.error(cmd_result)
                    return False
                target_files[index].move(image_file)

        return True


    def _process_tags_from_meta(self, m, source_files):
        """
        No processing ... this is just a copy
        """
        source_file = source_files['tag'].get('absolute')
        target_file = self.processed_files_manager.get_processed_file(m.source_hash, 'tags')

        if not source_file:
            log.warn('No tag file provided')
            return False
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

    parser.add_argument('--process_order_function', choices=PROCESS_ORDER_FUNCS.keys(), help='', default=DEFAULT_ORDER_FUNC)

    args_dict = parse_args(parser)

    args_dict['process_order_function'] = PROCESS_ORDER_FUNCS[args_dict['process_order_function']]

    return args_dict


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(encode_media, **args)
