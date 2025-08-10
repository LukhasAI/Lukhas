import json

import matplotlib.pyplot as plt


def generate_report(data):
    """
    Generates a validation report in Markdown format.

    Args:
        data: A list of dictionaries, where each dictionary represents a validation scenario.
    """

    report = ""

    # Add a title to the report.
    report += "# Validation Report\n\n"

    # Add a summary of the validation scenarios.
    report += "## Validation Scenarios\n\n"
    report += "| Scenario ID | Description | Result |\n"
    report += "|---|---|---|\n"
    for scenario in data:
        report += f"| {scenario['scenario_id']} | {scenario['description']} | {scenario['result']} |\n"
    report += "\n"

    # Add a summary of the metrics.
    report += "## Metrics\n\n"
    for scenario in data:
        report += f"### {scenario['scenario_id']}\n\n"
        for metric, values in scenario["metrics"].items():
            report += f"#### {metric}\n\n"
            # Generate a plot for the metric.
            plt.figure()
            plt.plot(values)
            plt.title(f"{metric} for {scenario['scenario_id']}")
            plt.xlabel("Time")
            plt.ylabel(metric)
            plt.savefig(f"{scenario['scenario_id']}_{metric}.png")
            plt.close()

            # Add the plot to the report.
            report += f"![{metric} for {scenario['scenario_id']}]({scenario['scenario_id']}_{metric}.png)\n\n"

    # Return the report.
    return report


if __name__ == "__main__":
    # Load the validation data.
    with open("validation_results.json") as f:
        data = json.load(f)

    # Generate the report.
    report = generate_report(data)

    # Save the report to a file.
    with open("validation_report.md", "w") as f:
        f.write(report)
