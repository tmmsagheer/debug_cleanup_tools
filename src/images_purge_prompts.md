# Initial Prompt
# ------------------------------------------------------------------------------------------------
Do you propose the purge to happen before the images are created so that only the latest analyzed images are stored and everything else is removed? Or should we create a separate script that monitors for items and periodically cleans them up to not exceed say 500 MB of storage? 
# Output
I strongly advise against a blanket "purge before creation" approach, and instead recommend Option B: A separate, quota-based Garbage Collection (GC) script.

Here is the architectural reasoning for this recommendation:

    The Parallel Execution Race Condition: n8n often evaluates multiple assets simultaneously or in rapid succession via Split In Batches nodes. If your engine purges the /output/images directory right before rendering RELIANCE, it will inadvertently delete the SBIN images that n8n is actively trying to attach to a webhook or Telegram message.

    Audit Trails: In quantitative development, maintaining a rolling buffer of recent visual artifacts is critical. If a strategy produces a false-positive buy signal, you need the historical render from the exact moment of execution to debug the OLS state logic. A pre-run purge destroys this forensic data.

The Solution: Least Recently Used (LRU) Garbage Collection

The standard practice is to deploy a standalone artifact manager. It calculates the directory size in megabytes and selectively deletes the oldest files until the directory drops below a safe threshold (e.g., 90% of your 500 MB limit, to prevent continuous execution thrashing).

Create a new file in your /src directory named artifact_manager.py.
Integration Strategy

Because this manager operates completely independently of the mathematical trading engine, it will not disrupt stdout or slow down n8n's critical-path execution time.

You have two optimal integration vectors:

    System Cron (Recommended): Add a rule to your Linux crontab to run this script asynchronously once every night at midnight.
    0 0 * * * /home/zf/anaconda3/envs/trading_engine_smm01_pipeline/bin/python /path/to/trading_engine/src/artifact_manager.py --limit 500 --target 400

    n8n Schedule Node: Create a simple, parallel workflow in n8n containing a Schedule Node (set to trigger daily) linked to an Execute Command node running the same CLI command.
# ------------------------------------------------------------------------------------------------
# Add-on prompt 1
N8N is the preferred option. Will the script also output the status of garbage collection as a JSON that can be parsed, let us say with helpful details like how many files it purged, what is the available memory after purge, what was it before, how much time it took, etc? 
# Output
Integrating the Garbage Collection (GC) module directly into n8n is the superior architectural choice. It centralizes pipeline observability, allowing you to trigger alerts or halt subsequent rendering nodes if storage anomalies are detected.

To achieve this, the GC script must be refactored to treat stdout as a sterile JSON data pipe, mirroring the design of the primary trading engine. Telemetry (timing, byte deltas, deletion counts) will be accumulated during execution and dumped as a serialized payload upon termination.

Here is the production-ready implementation of the JSON-compliant artifact manager.
Update /src/artifact_manager.py

Replace the previous GC script with this version. It strictly enforces file-only logging, calculates precise storage deltas, tracks execution time, and outputs an n8n-compatible JSON payload.
n8n Integration Protocol

To integrate this into n8n, create a standalone workflow completely decoupled from your 1-minute trading engine logic.

    Schedule Trigger Node: Set this to execute daily at a low-volume time (e.g., 00:00).

    Execute Command Node: Connect it to the Schedule Trigger. Use the following explicit CLI command to invoke the manager. Adjust the paths according to your n8n container or local environment bindings:

Bash

python3 /path/to/trading_engine/src/artifact_manager.py --dir /path/to/trading_engine/output/images --limit 500.0 --target 400.0

Expected JSON Output Schemas

n8n will parse the stdout automatically. You will encounter two operational states.

State 1: Nominal (No Purge Required)
Occurs when the directory size is safely below the --limit.
JSON

{
  "status": "Nominal",
  "directory": "/path/to/trading_engine/output/images",
  "files_purged": 0,
  "size_before_mb": 312.45,
  "size_after_mb": 312.45,
  "quota_limit_mb": 500.0,
  "execution_time_ms": 2.14
}

State 2: Purged (Quota Exceeded)
Occurs when the directory breaches the 500 MB limit, forcing the algorithm to delete the oldest images until the directory compresses to the 400 MB --target.
JSON

{
  "status": "Purged",
  "directory": "/path/to/trading_engine/output/images",
  "files_purged": 142,
  "size_before_mb": 508.12,
  "size_after_mb": 399.85,
  "quota_limit_mb": 500.0,
  "execution_time_ms": 18.45
}
# ------------------------------------------------------------------------------------------------