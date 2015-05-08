#
# PDSImage.py -- Loading a PDS Image
#

from ginga.BaseImage import BaseImage
import gdal_pds


class PDSImage(BaseImage):

    def __init__(self, data_np=None, metadata=None, logger=None):
        BaseImage.__init__(self, data_np=data_np, metadata=metadata,
                           logger=logger)

    def load_file(self, filepath):
        self.logger.debug("Loading file '%s' ..." % (filepath))
        pds_image = gdal_pds.PDSImage(filepath)
        self.pds_image = pds_image
        self.set_data(pds_image.image)
