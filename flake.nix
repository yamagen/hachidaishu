{
  description = "Python Shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-parts.url  = "github:hercules-ci/flake-parts";
  };

  outputs = { self, nixpkgs, flake-utils, flake-parts }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.python312
            pkgs.uv
            pkgs.zlib
            pkgs.stdenv.cc.cc.lib
          ];
          
          shellHook = ''
            export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
              pkgs.zlib
              pkgs.stdenv.cc.cc.lib
            ]}:$LD_LIBRARY_PATH            

            if [ -d .venv ]; then
              source .venv/bin/activate
            fi
            
            echo "uv version: $(uv --version)"
            echo "python version: $(python --version)"
          '';
        };
      });
}
