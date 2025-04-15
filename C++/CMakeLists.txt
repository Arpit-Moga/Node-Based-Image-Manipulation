cmake_minimum_required(VERSION 3.10)
project(NodeBasedImageEditor)

set(CMAKE_CXX_STANDARD 17)

# Find OpenCV
find_package(OpenCV REQUIRED)
find_package(OpenGL REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_search_module(GLFW REQUIRED glfw3)

# Include directories
include_directories(
    ${OpenCV_INCLUDE_DIRS}
    ${GLFW_INCLUDE_DIRS}
    ${OPENGL_INCLUDE_DIR}
    imgui
    imgui/backends
)

# ImGui source files
set(IMGUI_SOURCES
    imgui/imgui.cpp
    imgui/imgui_draw.cpp
    imgui/imgui_widgets.cpp
    imgui/imgui_tables.cpp
    imgui/imgui_demo.cpp
    imgui/backends/imgui_impl_glfw.cpp
    imgui/backends/imgui_impl_opengl3.cpp
)

# Your source files
set(SOURCES
    main.cpp
    gui.cpp
)

add_executable(NodeEditor ${SOURCES} ${IMGUI_SOURCES})

target_link_libraries(NodeEditor
    ${OpenCV_LIBS}
    ${GLFW_LIBRARIES}
    ${OPENGL_LIBRARIES}
    glfw
    GL
    dl
)





# cmake_minimum_required(VERSION 3.10)
# project(NodeEditor)

# set(CMAKE_CXX_STANDARD 17)

# # OpenCV
# find_package(OpenCV REQUIRED)

# # GLFW
# find_package(PkgConfig REQUIRED)
# pkg_search_module(GLFW REQUIRED glfw3)

# # GLAD/GL (optional if using GLEW instead)
# find_package(OpenGL REQUIRED)

# include_directories(
#     ${OpenCV_INCLUDE_DIRS}
#     ${GLFW_INCLUDE_DIRS}
#     ${CMAKE_SOURCE_DIR}/imgui
#     ${CMAKE_SOURCE_DIR}/imgui/backends
# )

# file(GLOB IMGUI_SRC
#     imgui/*.cpp
#     imgui/backends/imgui_impl_glfw.cpp
#     imgui/backends/imgui_impl_opengl3.cpp
# )

# add_executable(NodeEditor
#     gui.cpp
#     node_image_editor.cpp
#     ${IMGUI_SRC}
# )

# target_link_libraries(NodeEditor
#     ${OpenCV_LIBS}
#     ${GLFW_LIBRARIES}
#     OpenGL::GL
#     glfw
# )
