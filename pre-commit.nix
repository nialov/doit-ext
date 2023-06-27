{ pkgs, ... }: {
  src = ./.;
  hooks = {
    nixfmt.enable = true;
    black.enable = true;
    isort = {
      enable = true;
      raw = { args = [ "--profile" "black" ]; };
    };
    statix = { enable = true; };
    deadnix.enable = true;
    editorconfig-checker.enable = true;
    commitizen.enable = true;
    trim-trailing-whitespace = {
      enable = true;

      name = "trim-trailing-whitespace";
      description = "This hook trims trailing whitespace.";
      entry =
        "${pkgs.python3Packages.pre-commit-hooks}/bin/trailing-whitespace-fixer";
      types = [ "text" ];
    };
    check-added-large-files = {
      enable = true;

      name = "check-added-large-files";
      description = "This hook checks for large added files.";
      entry =
        "${pkgs.python3Packages.pre-commit-hooks}/bin/check-added-large-files --maxkb=5000";
    };
  };
}
