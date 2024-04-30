{ pkgs ? import <nixpkgs> {
    config.allowUnfree = true;
  } 
}:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs.buildPackages; [ 
      git 
      gnumake 
      libgcc 
      python3 
      python311Packages.matplotlib 
      python311Packages.tensorflow 
      python311Packages.numpy 
    ];
}