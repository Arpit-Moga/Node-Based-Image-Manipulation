cmake_minimum_required(VERSION 3.10)
project(NodeEditor)

set(CMAKE_CXX_STANDARD 17)

# OpenCV
find_package(OpenCV REQUIRED)

# GLFW
find_package(PkgConfig REQUIRED)
pkg_search_module(GLFW REQUIRED glfw3)

# GLAD/GL (optional if using GLEW instead)
find_package(OpenGL REQUIRED)

include_directories(
    ${OpenCV_INCLUDE_DIRS}
    ${GLFW_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}/imgui
    ${CMAKE_SOURCE_DIR}/imgui/backends
)

file(GLOB IMGUI_SRC
    imgui/*.cpp
    imgui/backends/imgui_impl_glfw.cpp
    imgui/backends/imgui_impl_opengl3.cpp
)

add_executable(NodeEditor
    gui.cpp
    node_image_editor.cpp
    ${IMGUI_SRC}
)

target_link_libraries(NodeEditor
    ${OpenCV_LIBS}
    ${GLFW_LIBRARIES}
    OpenGL::GL
    glfw
)
