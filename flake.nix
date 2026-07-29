{
  description = "Изолированное окружение для RAG Python проекта";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        
        packages = [
          pkgs.python312
          pkgs.uv
          pkgs.git
        ];

        buildInputs = [
          pkgs.stdenv.cc.cc.lib 
          pkgs.zlib
        ];

        shellHook = ''
          echo "🤖 RAG Development Environment Active!"
          echo "Python: $(python --version)"
          echo "uv:     $(uv --version)"

          export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"

          if [ ! -d .venv ]; then
            echo "📦 Создание venv через uv..."
            uv venv
          fi
          
          source .venv/bin/activate
        '';
      };
    };
}