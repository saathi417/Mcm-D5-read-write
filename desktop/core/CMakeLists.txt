cmake_minimum_required(VERSION 3.15)
project(mcm_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Builds 'mcmcore' as a shared library (mcmcore.dll on Windows). The C# WPF
# app loads it via P/Invoke, so place the built DLL next to the app binary.
add_library(mcmcore SHARED src/mcm_core.cpp)
target_include_directories(mcmcore PUBLIC include)

set_target_properties(mcmcore PROPERTIES
    OUTPUT_NAME "mcmcore"
    PREFIX ""        # avoid the "lib" prefix so the name matches DllImport
)

# Optional smoke test (built with -DMCM_BUILD_TESTS=ON).
option(MCM_BUILD_TESTS "Build the core self-test" OFF)
if(MCM_BUILD_TESTS)
    add_executable(mcm_core_test test/mcm_core_test.cpp)
    target_link_libraries(mcm_core_test PRIVATE mcmcore)
    enable_testing()
    add_test(NAME mcm_core_test COMMAND mcm_core_test)
endif()
