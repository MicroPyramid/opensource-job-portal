from sorl.thumbnail.base import ThumbnailBackend, EXTENSIONS
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import tokey, serialize
import os.path
import logging
import os
from sorl.thumbnail import default
from sorl.thumbnail.parsers import parse_geometry

logger = logging.getLogger(__name__)


class SEOThumbnailBackend(ThumbnailBackend):
    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.key, geometry_string, serialize(options))
        filename, _ext = os.path.splitext(os.path.basename(source.name))

        path = "%s/%s" % (key, filename)
        return "%s%s.%s" % (
            settings.THUMBNAIL_PREFIX,
            path,
            EXTENSIONS[options["format"]],
        )

    def _create_thumbnail(self, source_image, geometry_string, options, thumbnail):
        """
        Creates the thumbnail by using default.engine
        """
        source_image = source_image.convert("RGB")
        logger.debug(
            "Creating thumbnail file [%s] at [%s] with [%s]",
            thumbnail.name,
            geometry_string,
            options,
        )
        ratio = default.engine.get_image_ratio(source_image, options)
        geometry = parse_geometry(geometry_string, ratio)
        image = default.engine.create(source_image, geometry, options)
        default.engine.write(image, options, thumbnail)
        # It's much cheaper to set the size here
        size = default.engine.get_image_size(image)
        thumbnail.set_size(size)
