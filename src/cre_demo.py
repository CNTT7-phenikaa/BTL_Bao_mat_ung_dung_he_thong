import os
import pandas as pd

data = "..\\data\\raw\\cicids2017_500k.csv"
data_output = "..\\data\\demo"

os.makedirs(data_output, exist_ok=True)

benign_sp = []
attack_sp = []


for x in pd.read_csv(data):
    x.columns = x.columns.str.strip()

    benign = x[x["Label"] == "BENIGN"]
    attack = x[x["Label"] != "BENIGN"]

    if len(benign) > 0:
        benign_sp.append(benign.sample(
            n=min(100, len(benign)),
            random_state=42
        ))

    if len(attack) > 0:
        attack_sp.append(attack.sample(
            n=min(100, len(attack)),
            random_state=42
        ))

benign_df = pd.concat(benign_sp, ignore_index=True)
attack_df = pd.concat(attack_sp, ignore_index=True)

demo_benign = benign_df.sample(n=300, random_state=42)
demo_attack = attack_df.sample(n=300, random_state=42)

demo_mixed = pd.concat([
    benign_df.sample(n=250, random_state=42),
    attack_df.sample(n=50, random_state=42)
]).sample(frac=1, random_state=42)

demo_high_risk = pd.concat([
    benign_df.sample(n=100, random_state=42),
    attack_df.sample(n=200, random_state=42)
]).sample(frac=1, random_state=42)

demo_benign.to_csv(f"{data_output}/demo_benign.csv", index=False, encoding="utf-8-sig")
demo_attack.to_csv(f"{data_output}/demo_attack.csv", index=False, encoding="utf-8-sig")
demo_mixed.to_csv(f"{data_output}/demo_mixed.csv", index=False, encoding="utf-8-sig")
demo_high_risk.to_csv(f"{data_output}/demo_high_risk.csv", index=False, encoding="utf-8-sig")
