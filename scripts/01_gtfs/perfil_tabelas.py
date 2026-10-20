import pandas as pd, sys, os
D=sys.argv[1]
def r(n): return pd.read_csv(os.path.join(D,n+'.txt'),dtype=str,keep_default_na=False)
for n in ['routes','trips','stops','stop_times','frequencies','shapes','fare_rules']:
    df=r(n); print(f"\n===== {n}: {len(df):,} rows x {df.shape[1]} cols")
    for c in df.columns:
        s=df[c]; empty=(s.str.strip()=='').sum(); nu=s.nunique()
        top=s.value_counts().head(4)
        ws=(s!=s.str.strip()).sum()
        print(f"  {c:22s} empty={empty/len(s):6.1%} distinct={nu:>9,} ws={ws} top={dict(top) if nu<len(s)*0.9 else '-'}")
