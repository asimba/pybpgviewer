
set(BPGThumbnailer_SRCS bpgthumbnailer.cc)

kde4_add_plugin(bpgthumbnailer ${BPGThumbnailer_SRCS})

target_link_libraries(bpgthumbnailer bpg ${KDE4_KIO_LIBS})

install(TARGETS bpgthumbnailer DESTINATION ${PLUGIN_INSTALL_DIR} )

install(FILES bpgthumbnailer.desktop DESTINATION ${SERVICES_INSTALL_DIR})
