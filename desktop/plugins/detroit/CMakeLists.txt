cmake_minimum_required(VERSION 3.15)
project(DetroitPlugin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Read-only OEM decode/identify plugin. Builds DetroitPlugin.dll exporting
# CreatePlugin/DestroyPlugin. Needs the core's headers for IEcuPlugin.
add_library(DetroitPlugin SHARED DetroitPlugin.cpp)
target_include_directories(DetroitPlugin PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include)
set_target_properties(DetroitPlugin PROPERTIES PREFIX "")
