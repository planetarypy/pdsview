#
# PDSImage.py -- Loading a PDS Image
#

from ginga.BaseImage import BaseImage
from planetaryimage import PDS3Image


class PDSImage(BaseImage):

    def __init__(self, data_np=None, metadata=None, logger=None):
        BaseImage.__init__(self, data_np=data_np, metadata=metadata,
                           logger=logger)

    def load_file(self, filepath):
        self.logger.debug("Loading file '%s' ..." % (filepath))
        pds_image = PDS3Image.open(filepath)
        self.pds_image = pds_image
        self.set_data(pds_image.data)
        with open(filepath) as f:
            labelview = []
            for lineno, line in enumerate(f):
                line = line.rstrip()
                if line.strip() == 'END':
                    break
                labelview.append(line)
        pds_image.labelview = labelview
