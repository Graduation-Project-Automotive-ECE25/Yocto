DESCRIPTION = "Lane Detection Module using OpenCV"
LICENSE = "CLOSED"

# Specify the source file
SRC_URI = "file://lane-detection.py"

# Define where to extract source files
S = "${WORKDIR}"

# Dependencies (Ensure OpenCV is installed)
DEPENDS = "opencv"

do_install() {
    install -d ${D}${bindir}
    install -m 0755 lane-detection.py ${D}${bindir}/lane-detection
}

FILES_${PN} = "${bindir}/lane-detection"

# Enable runtime dependencies for OpenCV and Python
RDEPENDS_${PN} = "opencv python3-core"
