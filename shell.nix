let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  buildInputs = [
    pkgs.python3
  ];
  shellHook = ''
    export OPENAI_API_KEY="<PUT_KEY_HERE>"

    activate() {
      python3 -m venv env
      source env/bin/activate
      pip install -r requirements.txt
    }

    freeze_deps() {
      pip freeze > requirements.txt
    }

    activate
  '';
}
