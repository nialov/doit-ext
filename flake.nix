{
  description = "nix declared development environment";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    nixpkgs-copier.url =
      "github:nialov/nixpkgs?rev=334c000bbbc51894a3b02e05375eae36ac03e137";
    poetry2nix-copier.url =
      "github:nialov/poetry2nix?rev=6711fdb5da87574d250218c20bcd808949db6da0";
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

        devShellPackages = with pkgs; [ pre-commit pandoc poetry ];

      in {
        checks = {
          inherit (self.packages."${system}") doit-ext doit-ext-docs;
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
          doit-ext-python =
            pkgs.python3.withPackages (p: with p; [ doit-ext doit ]);
          doit-ext-docs = let
            sphinxEnv = pkgs.python3.withPackages (p:
              with p; [
                doit-ext
                sphinx
                sphinx-autodoc-typehints
                sphinx-rtd-theme
              ]);
          in pkgs.runCommand "doit-ext-docs" { } ''
            tmpdir=$(mktemp -d)
            ln -s ${./doit_ext} $tmpdir/doit_ext
            cp -r ${./docs_src} $tmpdir/docs_src
            chmod -R 777 $tmpdir/docs_src
            cd $tmpdir
            ${sphinxEnv}/bin/sphinx-apidoc -o docs_src/apidoc -f doit_ext -e -f
            ${sphinxEnv}/bin/sphinx-build -b html docs_src/ $out
          '';
        };
        devShells = {
          default = pkgs.mkShell {
            packages = devShellPackages;
            inherit (self.checks.${system}.preCommitCheck) shellHook;
          };
          poetry = self.packages."${system}".poetryEnv.env;
        };
      }) // {
        overlays.default = _: prev: {
          pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
            (python-final: _: {
              doit-ext = python-final.callPackage ./default.nix { };
            })
          ];
        };
      };

}
