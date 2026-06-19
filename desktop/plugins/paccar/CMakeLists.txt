cmake_minimum_required(VERSION 3.15)
project(PaccarPlugin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Read-only OEM decode/identify plugin -> PaccarPlugin.dll.
add_library(PaccarPlugin SHARED PaccarPlugin.cpp)
target_include_directories(PaccarPlugin PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include)
set_target_properties(PaccarPlugin PROPERTIES PREFIX "")
