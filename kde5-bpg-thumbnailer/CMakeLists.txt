project(KdeBPGThumbnailer)

cmake_minimum_required(VERSION 3.9)
set(QT_MIN_VERSION "5.2.0")

find_package(ECM 1.0.0 REQUIRED NO_MODULE)

set(CMAKE_MODULE_PATH ${ECM_MODULE_PATH} ${ECM_KDE_MODULE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

find_package(Qt5Gui REQUIRED)
find_package(KF5 REQUIRED KIO)

include(FeatureSummary)
include(KDEInstallDirs)
include(KDECMakeSettings)
include(KDECompilerSettings)

set(BPGThumbnailer_SRCS src/bpgthumbnailer.cc)

add_library(bpgthumbnailer MODULE ${BPGThumbnailer_SRCS})
target_link_libraries(bpgthumbnailer Qt5::Gui KF5::KIOWidgets bpg)
install(TARGETS bpgthumbnailer DESTINATION ${LIB_INSTALL_DIR}/qt5/plugins)
install(FILES src/bpgthumbnailer.desktop DESTINATION ${SERVICES_INSTALL_DIR})
