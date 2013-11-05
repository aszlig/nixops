{ revision ? "local" }:

let

  pkgs = import <nixpkgs> {};

  systemModule = pkgs.lib.evalModules {
    modules = [ ../../nix/options.nix ./dummy.nix ];
    args = { inherit pkgs; utils = {}; };
    check = false;
  };

  optionsXML = builtins.toFile "options.xml" (builtins.unsafeDiscardStringContext
    (builtins.toXML (pkgs.lib.optionAttrSetToDocList systemModule.options)));

  optionsDocBook = pkgs.runCommand "options-db.xml" {} ''
    ${pkgs.libxslt}/bin/xsltproc \
      --stringparam revision '${revision}' \
      -o $out ${<nixpkgs/nixos/doc/manual/options-to-docbook.xsl>} ${optionsXML}
  '';

in optionsDocBook
