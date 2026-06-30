files = ["ui/batch_mode.py", "ui/single_mode.py"]
for fpath in files:
    with open(fpath, "r") as f:
        code = f.read()
    
    # insert self.engine
    from_str = "        super().__init__(root)\n"
    to_str = "        super().__init__(root)\n        from core.engine import RibGeneratorEngine\n        self.engine = RibGeneratorEngine()\n"
    code = code.replace(from_str, to_str)
    
    with open(fpath, "w") as f:
        f.write(code)

print("Added self.engine")
