{
  description = "nix declared development environment";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    nix-extra = {
      url = "github:nialov/nix-extra";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-utils.url = "github:numtide/flake-utils";
    pre-commit-hooks = { url = "github:cachix/pre-commit-hooks.nix"; };
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachSystem [ flake-utils.lib.system.x86_64-linux ] (system:
      let
        # Initialize nixpkgs for system
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            self.overlays.default
            inputs.nix-extra.overlays.default
            inputs.poetry2nix.overlays.default
          ];
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
            ln -s ${./README.rst} $tmpdir/README.rst
            cp -r ${./docs_src} $tmpdir/docs_src
            chmod -R 777 $tmpdir/docs_src
            cd $tmpdir
            ${sphinxEnv}/bin/sphinx-apidoc -o docs_src/apidoc -f doit_ext -e -f
            ${sphinxEnv}/bin/sphinx-build -b html docs_src/ $out
          '';
          sync-git-tag-with-poetry = pkgs.writeShellApplication {
            name = "sync-git-tag-with-poetry";
            runtimeInputs = with pkgs; [ poetry git coreutils gnused ];
            text = ''
              version="$(git tag --sort=-creatordate | head -n 1 | sed 's/v\(.*\)/\1/')"
              poetry version "$version"
            '';
          };
          update-changelog = pkgs.writeShellApplication {
            name = "update-changelog";
            runtimeInputs = with pkgs; [
              clog-cli
              ripgrep
              git
              gnused
              coreutils
              pandoc
            ];
            text = ''
              homepage="$(rg 'homepage =' pyproject.toml | sed 's/.*"\(.*\)"/\1/')"
              version="$(git tag --sort=-creatordate | head -n 1 | sed 's/v\(.*\)/\1/')"
              clog --repository "$homepage" --subtitle "Release Changelog $version" "$@"
            '';
          };
          pre-release = pkgs.writeShellApplication {
            name = "pre-release";
            runtimeInputs = [
              self.packages."${system}".update-changelog
              self.packages."${system}".sync-git-tag-with-poetry
            ];
            text = ''
              sync-git-tag-with-poetry
              update-changelog --changelog CHANGELOG.md
              pandoc CHANGELOG.md --from markdown --to markdown --output CHANGELOG.md
            '';

          };
          poetry-run = pkgs.writeShellApplication {
            name = "poetry-run";
            runtimeInputs =
              self.devShells."${system}".default.nativeBuildInputs;
            text = ''
              poetry check
              poetry env use "$1"
              shift
              poetry env info
              poetry lock --check
              poetry install
              poetry run "$@"
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
      }) // {
        overlays.default = _: prev: {
          pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
            (python-final: _: {
              doit-ext = python-final.callPackage ./default.nix { };
            })
          ];

          inherit (self.packages."${prev.system}")
            update-changelog sync-git-tag-with-poetry poetryEnv;

        };
      };

}
