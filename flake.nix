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

        devShellPackages = with pkgs; [ pre-commit pandoc ];

      in {
        packages.doit-ext = pkgs.python3Packages.doit-ext;
        packages.doit-ext-python =
          pkgs.python3.withPackages (p: with p; [ doit-ext doit ]);
        # (with pkgs; {
        # inherit (python3.pkgs)
        #   buildPythonPackage pytestCheckHook poetry-core pytest-regressions;
        # inherit (pkgs) poetry2nix;
        # });
        checks = {
          inherit (self.packages."${system}") doit-ext;
          preCommitCheck = inputs.pre-commit-hooks.lib.${system}.run
            (import ././pre-commit.nix { inherit pkgs; });

        };
        packages.default = self.packages."${system}".doit-ext;
        devShells.default = pkgs.mkShell {
          packages = devShellPackages;
          inherit (self.checks.${system}.preCommitCheck) shellHook;

        };
      }) // {
        overlays.default = _: prev: {
          pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
            (python-final: _: { doit-ext = python-final.callPackage ./. { }; })
          ];
        };
      };

}
