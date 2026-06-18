cmake_minimum_required(VERSION 3.15)
project(NativeEngine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Reuse the decode core from desktop/core.
set(CORE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../core)

add_library(NativeEngine SHARED
    src/native_engine.cpp
    ${CORE_DIR}/src/mcm_core.cpp
)
target_include_directories(NativeEngine PUBLIC include ${CORE_DIR}/include)
set_target_properties(NativeEngine PROPERTIES PREFIX "")

option(MCM_BUILD_TESTS "Build the NativeEngine self-test" OFF)
if(MCM_BUILD_TESTS)
    add_executable(native_engine_test test/native_engine_test.cpp)
    target_link_libraries(native_engine_test PRIVATE NativeEngine)
    enable_testing()
    add_test(NAME native_engine_test COMMAND native_engine_test)
endif()
