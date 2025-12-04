import os
from collections import defaultdict

import requests

URL = "https://api.github.com/repos/rmj3197/SurVigilance/actions/workflows/coverage.yml/runs?per_page=100"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "daily_status.rst")


def main():
    try:
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return
        runs = response.json().get("workflow_runs", [])
    except Exception as e:
        print(f"Error: {e}")
        return

    daily_runs = defaultdict(list)
    for run in runs:
        date = run["created_at"].split("T")[0]
        daily_runs[date].append(run)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("============\n")
        f.write("Daily Status\n")
        f.write("============\n\n")
        f.write(
            "This page displays the execution status of the `coverage.yml` workflow, located at `https://github.com/rmj3197/SurVigilance/blob/master/.github/workflows/coverage.yml`. It runs daily at 12:00 AM UTC and provides an overview of the tool's operational status and potential issues.\n\n"
        )
        f.write(".. list-table:: Workflow Runs\n")
        f.write("   :header-rows: 1\n\n")
        f.write("   * - Date\n")
        f.write("     - Result\n")
        f.write("     - Details\n")

        for date in sorted(daily_runs.keys(), reverse=True):
            latest = sorted(
                daily_runs[date], key=lambda x: x["created_at"], reverse=True
            )[0]

            conclusion = latest["conclusion"]
            link = latest["html_url"]

            if conclusion == "success":
                icon = "✅ Pass"
            elif conclusion == "cancelled":
                icon = "⚠️ Cancelled"
            elif conclusion == "failure":
                icon = "❌ Fail"
            else:
                icon = "⚪ " + str(conclusion)

            f.write(f"   * - {date}\n")
            f.write(f"     - {icon}\n")
            f.write(f"     - `View Log <{link}>`_\n")


if __name__ == "__main__":
    main()
