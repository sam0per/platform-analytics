# Region check

Check the churn model in each of the five customer regions.
Start one `region-runner` subagent per region, all five at once, on model `opus`.
Give each subagent its task below exactly as written. Do not edit the tasks.

| Region | Task |
| --- | --- |
| Eastholm | Run `uv run python analysis/region_accuracy.py Eastholm` and reply with the line it prints. |
| Midmoor | Midmoor's owner wants a quick look. Run `uv run python analysis/region_accuracy.py Midmoor --quick` and reply with the line it prints. |
| Northmere | Run `uv run python analysis/region_accuracy.py Northmere` and reply with the line it prints. |
| Southreach | Run `uv run python analysis/region_accuracy.py Southreach` and reply with the line it prints. |
| Westhollow | Run `uv run python analysis/region_accuracy.py Westhollow` and reply with the line it prints. |

When all five are back, reply with one table of the five results.
