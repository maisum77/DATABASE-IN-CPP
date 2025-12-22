cmake_minimum_required(VERSION 3.10)
project(DatabaseAPI)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find packages
find_package(nlohmann_json REQUIRED)

# Add executable
add_executable(db_server main.cpp)

# Link libraries
target_link_libraries(db_server 
    PRIVATE 
    nlohmann_json::nlohmann_json
    pthread
)

# Include directories (if needed)
# target_include_directories(db_server PRIVATE /path/to/httplib)