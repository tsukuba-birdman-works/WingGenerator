import sys
import os
sys.path.append(os.getcwd())
from ui.batch_mode import BatchRunner

# Run the batch export
runner = BatchRunner()
runner.run_all()
