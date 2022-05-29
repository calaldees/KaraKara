## -*- coding: utf-8 -*-
import tempfile
import random
import re
from pathlib import Path

from clint.textui.progress import bar as progress_bar

from processmedia_libs import EXTS, PENDING_ACTION
from processmedia_libs.external_tools import ProcessMediaFilesWithExternalTools
from processmedia_libs.meta_overlay import MetaManagerExtended

from processmedia_libs.subtitle_processor_with_codecs import parse_subtitles
from processmedia_libs.subtitle_processor import create_vtt

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

def encode_media(process_order_function=PROCESS_ORDER_FUNCS[DEFAULT_ORDER_FUNC], **kwargs):
    meta_manager = MetaManagerExtended(**kwargs)  #path_meta=kwargs['path_meta'], path_source=kwargs['path_source']
    meta_manager.load_all()

    encoder = Encoder(meta_manager, **kwargs)

    for name in progress_bar(
        process_order_function(
            m.name for m in meta_manager.meta.values()
            if 
                PENDING_ACTION['encode'] in m.pending_actions  # if explitily marked for encoding
                or                                             # or
                not m.source_details.get('duration')           # no duration
        #(
            #'AKB0048 Next Stage - ED1 - Kono Namida wo Kimi ni Sasagu',
            #'Cuticle Tantei Inaba - OP - Haruka Nichijou no Naka de',
            #'Gosick - ED2 - Unity (full length)',
            #'Ikimonogakari - Sakura', # Takes 2 hours to encode
            #'Frozen Japanise (find real name)'  # took too long to process

            # 'Parasite Eve - Somnia Memorias',  # Non unicode characterset
            # 'Akira Yamaoka - Día de los Muertos',  # Non unicode characterset
            # 'Higurashi no Naku koro ni - ED - why or why not (full length)',  # When subs import from SSA they have styling information still attached
            # 'Gatekeepers - OP - For the Smiles of Tomorrow.avi',  # It's buggered. Looks like it's trying to containerize subs in a txt file?
            # 'Get Backers - ED2 - Namida no Hurricane', # It's just fucked
            # 'Nana (anime) - OP - Rose',  # SSA's have malformed unicode characters
            # 'Lunar Silver Star Story - OP - Wings (Japanese Version)',
            # 'Evangleion ED - Fly Me To The Moon',  # Odd dimensions and needs to be normalised
            # 'Ranma Half OP1 - Jajauma ni Sasenaide',
            # 'Tamako Market - OP - Dramatic Market Ride',
            # 'Fullmetal Alchemist - OP1 - Melissa',  # Exhibits high bitrate pausing at end
            # 'Samurai Champloo - OP - Battlecry',  # Missing title sub with newline
            # 'KAT-TUN Your side [Instrumental]',
        )
    ):
        try:
            encoder.encode(name)
        except Exception as ex:
            log.exception('Failed to encode {}'.format(name))


class Encoder(object):
    """
    """

    def __init__(self, meta_manager=None, heartbeat_file=None, **kwargs):  #  ,path_meta=None, path_processed=None, path_source=None, **kwargs
        self.meta_manager = meta_manager  # or MetaManagerExtended(path_meta=path_meta, path_source=path_source, path_processed=path_processed)  # This 'or' needs to go
        self.external_tools = ProcessMediaFilesWithExternalTools(
            **{k: v for k, v in kwargs.items() if k in ('cmd_ffpmeg', 'cmd_ffprobe', 'cmd_imagemagick_convert') and v}
        )
        self._heartbeat_file = Path(heartbeat_file) if heartbeat_file else None

    def heartbeat(self):
        if self._heartbeat_file:
            self._heartbeat_file.touch()

    def encode(self, name):
        """
        Todo: save the meta on return ... maybe use a context manager
        """
        log.info('Encode: %s', name)
        self.meta_manager.load(name)
        m = self.meta_manager.get(name)

        with tempfile.TemporaryDirectory() as self.tempdir:
            self._extract_source_details(m)  # get details from probing source and cache in metafile
            for target_file in m.processed_files.values():
                if target_file.file.is_file():
                    log.debug(f'{name}: {target_file.type.key} exists')
                    continue
                self._process_target_file(m, target_file)
                self.heartbeat()

            assert tuple(
                f'{name} - {f.type.key} - {f.relative}'
                for f in m.processed_files.values()
                if not f.file.is_file()
            ) == tuple(), 'Not all expected processed files were present'

            try:
                m.pending_actions.remove(PENDING_ACTION['encode'])
            except ValueError:
                pass
            self.meta_manager.save(name)


    def _extract_source_details(self, m):
        source_details = {}

        # Probe Image
        source_image = m.source_files.get('image')
        if source_image:
            source_details.update({
                k: v for k, v in self.external_tools.probe_media(source_image.file).items()
                if k in ('width', 'height')
            })

        # Probe Audio
        source_audio = m.source_files.get('audio')
        if source_audio:
            source_details.update({
                k: v for k, v in self.external_tools.probe_media(source_audio.file).items()
                if k in ('duration',)
            })

        # Probe Video
        source_video = m.source_files.get('video')
        if source_video:
            source_details.update(self.external_tools.probe_media(source_video.file))

        if not source_details.get('duration'):
            raise Exception(f'Unable to identify source duration. Maybe the source file is damaged? {m.name}')

        m.source_details.update(source_details)


    def _process_target_file(self, m, target_file):
        destination = Path(self.tempdir, f'{target_file.type.key}.{target_file.type.ext}')
        # Video
        if target_file.type.attachment_type in ('video', 'preview'):
            self.external_tools.encode_video(
                source=self._get_absolute_video_to_encode(m),
                destination=destination,
                encode_args=target_file.type.encode_args,
            ),
        # Image
        elif target_file.type.attachment_type in ('image',):
            index = re.match(r'image(\d)_.+', target_file.type.key).group(1)
            uncompressed_image_file = Path(self.tempdir, f'{index}.bmp')
            if not uncompressed_image_file.is_file():
                self.external_tools.extract_image(
                    source=self._get_absolute_video_to_encode(m),
                    destination=uncompressed_image_file,
                    encode_args=target_file.type.encode_args,
                    timecode=self._image_index_to_timecode(m, index),
                )
            self.external_tools.compress_image(
                source=uncompressed_image_file,
                destination=destination,
            )
        # Subtitle
        elif target_file.type.attachment_type in ('subtitle',):
            with m.source_files['sub'].file.open('rt') as filehandle:
                subtitles = parse_subtitles(filehandle=filehandle)
            if target_file.type.mime == 'text/vtt':
                with destination.open('wt') as filehandle:
                    filehandle.write(create_vtt(subtitles))
            else:
                raise Exception('unknown subtitle output type')
        # Unknown Error
        else:
            raise Exception(f'unknown target file {target_file.type}')
        target_file.move(destination)


    def _get_absolute_video_to_encode(self, m):
        source = None
        if m.source_files.get('video'):
            source = m.source_files.get('video').file
        target_file = m.processed_files['video']

        if m.source_files.get('image') and not source:
            source = Path(self.tempdir, f"image.{target_file.type.ext}")
            if not source.is_file():
                self.external_tools.encode_image_to_video(
                    video_source=m.source_files['image'].file,
                    audio_source=m.source_files['audio'].file,
                    destination=source,
                    encode_args=target_file.type.encode_args,
                    **m.source_details,
                )

        if not source:
            log.error('Unable to encode as no video was provided {}'.format(source))
            raise Exception()

        if not source.is_file():
            log.error('Video to encode does not exist {}'.format(source))
            raise Exception()

        return source


    def _image_index_to_timecode(self, m, index, num_images=4):
        source_file_absolute = self._get_absolute_video_to_encode(m)
        if Path(source_file_absolute).suffix.replace('.','') in EXTS['image']:
            # If source input is a single image, we use it as an input video and take
            # a frame 4 times from frame zero.
            # This feels inefficient, but we need 4 images for the import check.
            # Variable numbers of images would need more data in the meta
            times = (0, ) * num_images
        else:
            video_duration=m.source_details.get('duration')
            assert video_duration
            times = tuple(
                float("%.3f" % (video_duration * offset)) 
                for offset in (
                    x/(num_images+1) for x in range(1, num_images+1)
                )
            )
        return times[int(index)-1]



# Main -------------------------------------------------------------------------

def additional_arguments(parser):
    parser.add_argument('--process_order_function', choices=PROCESS_ORDER_FUNCS.keys(), help='', default=DEFAULT_ORDER_FUNC)


def process_arguments(kwargs):
    kwargs['process_order_function'] = PROCESS_ORDER_FUNCS[kwargs['process_order_function']]


if __name__ == "__main__":
    from _main import main
    main(
        'encode_media', encode_media, folder_type_to_derive_mtime='meta', version=VERSION,
        additional_arguments_function=additional_arguments,
        additional_arguments_processing_function=process_arguments,
    )
