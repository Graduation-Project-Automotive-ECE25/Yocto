SUMMARY = "My Qt6 QMake Application"
DESCRIPTION = "A QMake-based Qt6 application for Raspberry Pi"
LICENSE = "CLOSED"

# If your code is hosted on Git:
SRC_URI = "git://github.com/Graduation-Project-Automotive-ECE25/GUI.git;protocol=https;branch=master"
SRCREV = "50d51e47dedac45900ad3dfb52c4e6942f8f02a2"

# QMAKE-based build for Qt6
inherit qt6-qmake

# Add the Qt modules your app uses
DEPENDS = "qtbase qtdeclarative qtshadertools qtmultimedia qtserialport  qt5compat "
RDEPENDS:${PN} += "qtbase qtdeclarative qtserialport  qt5compat qtpositioning qtlocation  "

S = "${WORKDIR}/git"  

do_install:append() {
    install -d ${D}/opt/FinalDashboard_project/qml
    install -m 0644 ${S}/*.qml ${D}/opt/FinalDashboard_project/qml/
}

FILES:${PN} += "/opt/FinalDashboard_project/qml/*"

FILES:${PN} += "/opt/FinalDashboard_project/bin/FinalDashboard_project"
