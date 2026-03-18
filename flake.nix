{
  description = "React Development Environment";

  inputs = {
    # We pull from the unstable branch for the latest web tools
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux"; 
      pkgs = nixpkgs.legacyPackages.${system};

      mPython = pkgs.python3.withPackages (ps: with ps; [
        fastapi
        selenium
        sqlalchemy
        beautifulsoup4
        uvicorn
        bcrypt
        pyjwt
      ]);
        
      mJava = [
        pkgs.jdk21
        pkgs.maven
      ];

    in
    {
      devShells.${system}.default = pkgs.mkShell {
        # Packages added here will be available in your terminal
        buildInputs = with pkgs; [
          nodejs_22
          nodePackages.npm
          nodePackages.typescript-language-server
          # Optional: helpful for VS Code or Vim integration
          nodePackages.vscode-langservers-extracted 
    
          mPython

          jdt-language-server
          mJava

          docker
          docker-compose
          redis
        ] ++ mJava;

        # This runs every time you enter the shell
        shellHook = ''
          echo "✨ React + NixOS Dev Environment Loaded ✨"
          echo "Node version: $(node -v)"
        '';
      };
    };
}
