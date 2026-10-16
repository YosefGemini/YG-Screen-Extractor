
cmake_minimum_required(VERSION 3.16)

project(YGScreenExtractorCaptureHelper LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core DBus Gui)

include(GNUInstallDirs)

add_executable(yg-screen-extractor-capture-helper main.cpp)

target_link_libraries(yg-screen-extractor-capture-helper
    PRIVATE
        Qt6::Core
        Qt6::DBus
        Qt6::Gui
)

configure_file(
    io.github.screenocr.capture-helper.desktop.in
    ${CMAKE_CURRENT_BINARY_DIR}/io.github.screenocr.capture-helper.desktop
    @ONLY
)

install(
    TARGETS yg-screen-extractor-capture-helper
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/io.github.screenocr.capture-helper.desktop
    DESTINATION ${CMAKE_INSTALL_DATADIR}/applications
)
