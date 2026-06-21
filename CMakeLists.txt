set(Namespace_SRCS
        freecad/Fabric/init_gui.py
        freecad/Fabric/__init__.py
        freecad/Fabric/my_numpy_function.py
        freecad/Fabric/version.py
        freecad/Fabric/resources/cool.svg
        freecad/Fabric/resources/translations/Fabric_es-ES.qm
        freecad/Fabric/resources/translations/Fabric_es-ES.ts
)

SOURCE_GROUP("" FILES ${Namespace_SRCS})

ADD_CUSTOM_TARGET(SEARCHBAR ALL
        SOURCES ${Namespace_SRCS}
)

fc_copy_sources(SEARCHBAR "${CMAKE_BINARY_DIR}/Mod/Fabric" ${Namespace_SRCS})

INSTALL(
    FILES
        ${Namespace_SRCS}
    DESTINATION
        Mod/SearchBar
)
