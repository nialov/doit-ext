{
  description = "nix declared development environment";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pre-commit-hooks = { url = "github:cachix/pre-commit-hooks.nix"; };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachSystem [ flake-utils.lib.system.x86_64-linux ] (system:
      let
        # Initialize nixpkgs for system
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        };

        devShellPackages = with pkgs; [
          pre-commit
          pandoc
          poetry-with-c-tooling
          # Supported python versions
          python39
          python310
          python311
        ];

      in {
        checks = {
          inherit (self.packages."${system}") doit-ext;
          preCommitCheck = inputs.pre-commit-hooks.lib.${system}.run
            (import ././pre-commit.nix { inherit pkgs; });
        };
        packages = {
          default = self.packages."${system}".doit-ext;
          poetryEnv = pkgs.poetry2nix.mkPoetryEnv {
            projectDir = ./.;
            editablePackageSources = { doit_ext = ./doit_ext; };
          };
          inherit (pkgs.python3Packages) doit-ext;
          doit-with-ext =
            pkgs.python3.withPackages (p: with p; [ doit-ext doit ]);
          docs = let
            sphinxEnv = pkgs.python3.withPackages (p:
              with p; [
                doit-ext
                sphinx
                sphinx-autodoc-typehints
                sphinx-rtd-theme
              ]);
          in pkgs.runCommand "docs" { } ''
            tmpdir=$(mktemp -d)
            ln -s ${./doit_ext} $tmpdir/doit_ext
            cp -r ${./docs_src} $tmpdir/docs_src
            chmod -R 777 $tmpdir/docs_src
            cd $tmpdir
            ${sphinxEnv}/bin/sphinx-apidoc -o docs_src/apidoc -f doit_ext -e -f
            ${sphinxEnv}/bin/sphinx-build -b html docs_src/ $out
          '';
          sync-git-tag-with-poetry = pkgs.writeShellApplication {
            name = "sync-git-tag-with-poetry";
            runtimeInputs = with pkgs; [ poetry git coreutils ];
            text = ''
              version="$(git tag --sort=-creatordate | head -n 1 | sed 's/v\(.*\)/\1/')"
              poetry version "$version"
            '';
          };
          poetry-test-python = pkgs.writeShellApplication {
            name = "poetry-test-python";
            runtimeInputs =
              self.devShells."${system}".default.nativeBuildInputs;
            text = ''
              poetry check
              poetry env use "$1"
              poetry lock --check
              poetry install
              poetry run pytest
            '';

          };
          poetry-with-c-tooling = pkgs.symlinkJoin {
            name = "poetry-with-c-tooling";
            buildInputs = with pkgs; [ makeWrapper ];
            paths = with pkgs; [ poetry ];
            postBuild = let

              caBundle = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";
              ccLib = "${pkgs.stdenv.cc.cc.lib}/lib";
              zlibLib = "${pkgs.zlib}/lib";
              ldPath = "${ccLib}:${zlibLib}";
              wraps = [
                "--set GIT_SSL_CAINFO ${caBundle}"
                "--set SSL_CERT_FILE ${caBundle}"
                "--set CURL_CA_BUNDLE ${caBundle}"
                "--set LD_LIBRARY_PATH ${ldPath}"
              ];

            in ''
              wrapProgram $out/bin/poetry ${builtins.concatStringsSep " " wraps}
              $out/bin/poetry --help
            '';
          };
        };
        devShells = {
          default = pkgs.mkShell {
            packages = devShellPackages;
            inherit (self.checks.${system}.preCommitCheck) shellHook;
          };
          poetry = self.packages."${system}".poetryEnv.env;
        };
        apps = {
          sync-git-tag-with-poetry = inputs.flake-utils.lib.mkApp {
            drv = self.packages."${system}".sync-git-tag-with-poetry;
          };
          poetry-test-pythons = inputs.flake-utils.lib.mkApp {
            drv = self.packages."${system}".poetry-test-pythons;
          };
        };
      }) // {
        overlays.default = _: prev: {
          pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
            (python-final: _: {
              doit-ext = python-final.callPackage ./default.nix { };
            })
          ];
          inherit (self.packages."${prev.system}") poetry-with-c-tooling;
        };
      };

}
