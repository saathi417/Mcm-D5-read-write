cmake_minimum_required(VERSION 3.15)
project(CumminsPlugin LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Read-only OEM decode/identify plugin -> CumminsPlugin.dll.
add_library(CumminsPlugin SHARED CumminsPlugin.cpp)
target_include_directories(CumminsPlugin PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../../core/include)
set_target_properties(CumminsPlugin PROPERTIES PREFIX "")
