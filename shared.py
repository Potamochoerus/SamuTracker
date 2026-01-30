from pathlib import Path
import pandas as pd

app_dir = Path(__file__).parent
match_history = pd.read_csv(app_dir / "data" / "match_history.csv")
threshold_score = 100