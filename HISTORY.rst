.. :changelog:

History
-------

0.5.1 (2017-07-24)
-------------------

* Fixes bug in ROI creation

0.5.0 (2017-05-22)
-------------------

* Use QtPy and do not depend on PySide
* Create a histogram to apply cut levels

0.4.1 (2015-09-10)
---------------------

* Updated to work with ginga 2.5.
* Bug fixes.


0.4.0 (2015-08-30)
---------------------

* Clicking on a point in an image now shows the image coordinates and pixel
  value at that location.
* Right clicking and dragging on the image will now create a region of interest.
  Statistics about that region of interest are shown.
* Composite RGB images can now be displayed by using the new Channels dialog and
  checking the RGB toggle.


0.3.0 (2015-08-03)
---------------------

* Reworked to use an ImageSet and ImageStamp model to improve program flow and
  permit launching from other programs.


0.2.0 (2015-07-28)
---------------------

* Cleaned up with parts rewritten.
* Takes files as command line arguments.
* Handles mutiple images.


0.1.0 (2015-06-06)
---------------------

* First release on PyPI.
