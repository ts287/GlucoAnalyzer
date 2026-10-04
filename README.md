# DatabricksHackathonChallenge

Claude was used to create a master plan to help with timing and splitting up work between the team. The plan was followed loosely and used as a guideline to understand what tasks needed to be done. Here is the link to the plan: https://claude.ai/artifact/MNqeRcLEiRUUkHLWVc1e5i

Claude was also used to generate code to download the data from the website, https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/#files-panel, into Databricks. Here is the code that was generated: 

    import os, requests
    
    spark.sql("CREATE VOLUME IF NOT EXISTS workspace.default.glycemic_raw")
    
    BASE = "https://physionet.org/files/big-ideas-glycemic-wearable/1.1.3"
    DEST = "/Volumes/workspace/default/glycemic_raw"
    PID = "001"
    
    FILES = [
        f"Dexcom_{PID}.csv",
        f"Food_Log_{PID}.csv",
        f"HR_{PID}.csv",
        f"IBI_{PID}.csv",
        f"TEMP_{PID}.csv",
        f"EDA_{PID}.csv",
        f"ACC_{PID}.csv",   # ~838 MB
        f"BVP_{PID}.csv",   # ~1.3 GB
    ]
    
    def fetch(url, path):
        # Skip files that are already complete
        head = requests.head(url, timeout=60, allow_redirects=True)
        size = int(head.headers.get("Content-Length", 0))
        if size and os.path.exists(path) and os.path.getsize(path) == size:
            print(f"Already have {os.path.basename(path)}, skipping")
            return

    tmp = path + ".part"
    done = 0
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tmp, "wb") as out:
            for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                out.write(chunk)
                done += len(chunk)
                if size:
                    print(f"\r{os.path.basename(path)}: {done/1e6:,.0f} / {size/1e6:,.0f} MB", end="")
    os.replace(tmp, path)
    print(f"\nSaved {os.path.basename(path)}")

    # Shared file for all participants
    fetch(f"{BASE}/Demographics.csv", f"{DEST}/Demographics.csv")
    
    # Everything for participant 001
    os.makedirs(f"{DEST}/{PID}", exist_ok=True)
    for name in FILES:
        fetch(f"{BASE}/{PID}/{name}", f"{DEST}/{PID}/{name}")
    
    print("\nDone. Files in volume:")
    for f in sorted(os.listdir(f"{DEST}/{PID}")):
        print(f"  {f}: {os.path.getsize(f'{DEST}/{PID}/{f}')/1e6:,.1f} MB")

Used the following link to figure out how to style text in python uing html and inline css styling:
https://stackoverflow.com/questions/70932538/how-to-center-the-title-and-an-image-in-streamlit

Databricks Genie Agents was used to build the blood sugar analyzer agent which was made using the data from https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/001/#files-panel
Files 001,002,003,004, and 005 were used to create this site and the agent
