{
  description = "A flake for PiRail developement";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let 
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
          };
        };

        isDarwin = pkgs.stdenv.isDarwin;
        isLinux = pkgs.stdenv.isLinux;

        commonPackages = with pkgs; [
          git
          python3 
          python312Packages.matplotlib 
          python312Packages.numpy 
          python312Packages.multiprocess
          python312Packages.pip
          python312Packages.psutil
          nodejs_24
        ] ++ (with pkgs; pkgs.lib.optionals isLinux) [
          gnumake 
          libgcc
          python312Packages.tensorflow
        ];

        mkLinuxShells = pkgs: {
          default = pkgs.mkShell {
            name = "PiRailLinuxEnv";
            venvDir = "./.venv";
            buildInputs = commonPackages ++ (with pkgs; [
                python312Packages.venvShellHook
              ]);
            postVenvCreation = ''
              pip install PyTermGUI
              npm install -D vite@7.1.12
            '';
            shellHook = ''
            '';
          };
        };

        mkDarwinShells = pkgs: {
          default = pkgs.mkShell {
            name = "PiRailLinuxEnv";
            venvDir = "./.venv";
            buildInputs = commonPackages ++ (with pkgs; [
                python312Packages.venvShellHook
              ]);
            postVenvCreation = ''
              pip install PyTermGUI
              npm install -D vite@7.1.12
            '';
            shellHook = ''
            '';
          };
        };

        shells = if isLinux then mkLinuxShells pkgs else mkDarwinShells pkgs;

      in {
        devShells = shells;
        devShell = shells.default;
      }
    );
}
