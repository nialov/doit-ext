({ inputs, self, ... }:

  {
    perSystem = { self', config, system, pkgs, lib, ... }:
      let
        mkNixpkgs = nixpkgs:
          import nixpkgs {
            inherit system;
            overlays = [
              inputs.nix-extra.overlays.default
              (_: prev: {
                pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
                  (_: pythonPrev: {
                    "doit-ext" = pythonPrev.doit-ext.overridePythonAttrs
                      # Test with local source
                      (_: { src = self.outPath; });
                  })
                ];
              })

            ];
            config = { allowUnfree = true; };
          };

      in {
        _module.args.pkgs = mkNixpkgs inputs.nixpkgs;
        devShells = {
          default = pkgs.mkShell {
            buildInputs = lib.attrValues {
              python3-env = pkgs.python3.withPackages (p:
                p.doit-ext.propagatedBuildInputs
                ++ [ p.pytest p.pytest-regression ]);
            };
            shellHook = config.pre-commit.installationScript;
          };

        };

        pre-commit = {
          check.enable = true;
          settings.hooks = {
            nixfmt.enable = true;
            nbstripout.enable = true;
            isort = { enable = true; };
            shellcheck.enable = true;
            statix.enable = true;
            deadnix.enable = true;
            rstcheck.enable = true;
            yamllint = { enable = false; };
            commitizen.enable = true;
            ruff = { enable = true; };
          };

        };
        packages = {

          inherit (pkgs.python3Packages) doit-ext;
          default = self'.packages.doit-ext;

        };
        legacyPackages = pkgs;
      };

  })
