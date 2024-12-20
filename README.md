# Quantum Information Experiments

## Usage

1. Clone this repository to your preferred folder

   ```bash
   cd [YOUR_PREFERRED_FOLDER] && git clone https://github.com/ZureTz/quantum-information-experiment.git
   cd quantum-information-experiment
   ```

2. Set Python virtual environment (Highly recommened but optional)

   ```bash
   python -m venv .venv
   ```
   
   Then run the command based on your environment

   | Platform   | Shell                                   | Command to activate virtual environment |
   | :--------- | :-------------------------------------- | :-------------------------------------- |
   | POSIX      | bash/zsh                                | `$ source .venv/bin/activate`   |
   | POSIX			| fish       | `$ source .venv/bin/activate.fish`      |
   | POSIX			| csh/tcsh   | `$ source .venv/bin/activate.csh`       |
   | POSIX			| pwsh       | `$ .venv/bin/Activate.ps1`      |
   | Windows    | cmd.exe                                 | `C:\> .venv\Scripts\activate.bat` |
   | Windows    | PowerShell | `PS C:\> .venv\Scripts\Activate.ps1` |

3. Install dependencies

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Now you can use `pyqpanda` and `qiskit` to do what you want.

## Edit Config files

1. Copy config/config.toml.example to config/config.toml
```bash
cp config/config.toml.example config/config.toml
```