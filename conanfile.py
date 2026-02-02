from conan import ConanFile
from conan.tools.files import get, download, copy, mkdir, unzip, rename
from conan.tools.scm import Version
import os
import subprocess

class CudaInstallerConan(ConanFile):
    name = "cuda"
    version = "12.1.0"
    description = "NVIDIA CUDA Toolkit Installer"
    license = "NVIDIA CUDA EULA"
    settings = "os", "arch"
    
    def validate(self):
        # if self.settings.os != "Windows":
            # raise ConanInvalidConfiguration("This recipe is only for Windows.")
        pass

    def requirements(self):
        pass

    def build(self):
        # 1. Construct the download URL based on NVIDIA's patterns
        # Example for 12.1.0 on Windows x86_64
        url = "https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_531.14_windows.exe"
        installer_name = "cuda_installer.exe"
        
        self.output.info(f"Downloading CUDA installer: {url}")
        download(self, url, installer_name)

        # 2. Run the installer in silent mode to extract to the build folder
        # -s: Silent installation
        # -u: Unattended
        # -f: Target directory (we use self.build_folder)
        # Note: Extracting is often safer in Conan than full system installation
        install_dir = os.path.join(self.package_folder, "cuda_install")
        mkdir(self, install_dir)
        
        self.output.info("Extracting CUDA components...")
        self.run(f"{installer_name} -s -n -clean -directory=\"{install_dir}\"")



    def package(self):
        # Copy headers, libs, and binaries from the extracted folder to the package folder
        # Adjust these paths based on where the .exe extracts files
        copy(self, "*", src=os.path.join(self.build_folder, "cuda_install"), dst=self.package_folder)

    def package_info(self):
        # This part mimics libhal/llvm-toolchain: defining environment variables for consumers
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib/x64"]
        self.cpp_info.bindirs = ["bin"]

        # Set CUDA_PATH so CMake's FindCUDA or FindCUDAToolkit can find it
        self.buildenv_info.define_path("CUDA_PATH", self.package_folder)
        self.runenv_info.define_path("CUDA_PATH", self.package_folder)
        
        # Add the bin directory to the PATH so nvcc can be called
        self.buildenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))