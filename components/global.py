# This defines some internal global state
# Identifying the system and then providing a way to search for compilers
import os
import platform

class State:
    def __init__(self):
        self.os_name = platform.system().lower()
        self.architecture = platform.machine().lower()        
        self.compiler_paths = self._set_default_paths()

    def _set_default_paths(self):
        paths = {
            "windows": [
                r"C:\Program Files\LLVM\bin",
                r"C:\MinGW\bin",
                r"C:\TDM-GCC-64\bin",
                r"C:\Windows\System32",
                r"C:\Windows",
            ],
            "linux": [
                "/usr/bin",
                "/usr/local/bin",
                "/opt/bin",
            ],
            "darwin": [  # macOS
                "/usr/bin",
                "/usr/local/bin",
                "/opt/homebrew/bin",
            ],
        }
        return paths.get(self.os_name, [])

    def search_compiler(self, compiler_name):
        if self.os_name == "windows":
            compiler_name = self._find_windows_executable(compiler_name)
        
        for path in self.compiler_paths:
            compiler_path = os.path.join(path, compiler_name)
            if os.path.isfile(compiler_path):
                return compiler_path
        
        for path in os.getenv('PATH', '').split(os.pathsep):
            compiler_path = os.path.join(path, compiler_name)
            if os.path.isfile(compiler_path):
                return compiler_path
        
        return None
    
    # windows being "different"
    def _find_windows_executable(self, compiler_name):
        for ext in ['.exe', '.bat', '.cmd']:
            if compiler_name.endswith(ext):
                return compiler_name
            else:
                potential_name = compiler_name + ext
                for path in os.getenv('PATH', '').split(os.pathsep):
                    if os.path.isfile(os.path.join(path, potential_name)):
                        return potential_name
        return compiler_name

    def __str__(self):
        return f"OS: {self.os_name}, Architecture: {self.architecture}, Compiler Paths: {self.compiler_paths}"

