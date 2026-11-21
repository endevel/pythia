from pythia.cmd.run_engine import RunEngine

def main() -> None:
    print("Hello from pythia!")
    cmd = RunEngine()
    cmd.execute(lambda: None)
