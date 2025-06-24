# This image is based on core-image-sato
require recipes-sato/images/core-image-sato.bb

# Only produce the "rpi-sdimg" image format
IMAGE_FSTYPES = "rpi-sdimg"

# Add our apps
IMAGE_INSTALL:append = "Dashboard"
IMAGE_INSTALL:append = "opencv lane-detection"
