# shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    libuldaq
  # Add these python packages:
  (pkgs.python3.withPackages (ps: with ps; [ numpy matplotlib ]))
  ];

  # This is the magic sauce: tell Python where to find libuldaq.so
  LD_LIBRARY_PATH = "${pkgs.libuldaq}/lib";
  
  shellHook = ''
    # Create a virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
      echo "Creating virtual environment..."
      python -m venv .venv
    fi
    
    # Activate the virtual environment
    source .venv/bin/activate
    
    # Install the Python bindings
    pip install uldaq
    
    echo "Environment ready. Run your script with 'python your_script.py'"
  '';
}
