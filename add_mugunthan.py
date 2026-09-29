import subprocess
import json
import time

PROJECT_ID = "project-4e3f1563-833a-4721-bf7"

print("Creating Mugunthan channel...")
cmd = f'gcloud beta monitoring channels create --display-name="Mugunthan (Cloud Run)" --type=email --channel-labels=email_address="mt.mugunthan@gmail.com" --project={PROJECT_ID} --format="value(name)"'
mugunthan_channel = subprocess.check_output(cmd, shell=True, text=True).strip()
print(f"Created channel: {mugunthan_channel}")

print("Fetching existing Cloud Run policy...")
cmd = f"gcloud alpha monitoring policies list --project={PROJECT_ID} --format=json"
out = subprocess.check_output(cmd, shell=True, text=True)
policies = json.loads(out)
cr_policy = None
for p in policies:
    if p.get("displayName") == "Cloud Run 5xx Errors (Babu)":
        cr_policy = p
        break

if not cr_policy:
    print("Cloud Run policy not found!")
    exit(1)

# Add Mugunthan to the policy
if mugunthan_channel not in cr_policy.get("notificationChannels", []):
    if "notificationChannels" not in cr_policy:
        cr_policy["notificationChannels"] = []
    cr_policy["notificationChannels"].append(mugunthan_channel)

# Rename to include Mugunthan
cr_policy["displayName"] = "Cloud Run 5xx Errors (Babu & Mugunthan)"

# We must remove some output-only fields before updating
for field in ["name", "creationRecord", "mutationRecord"]:
    if field in cr_policy:
        del cr_policy[field]

with open("alerts/cloud_run_policy_update.json", "w") as f:
    json.dump(cr_policy, f)

print("Updating policy...")
update_cmd = f"gcloud alpha monitoring policies update {p['name']} --policy-from-file=alerts/cloud_run_policy_update.json"
subprocess.run(update_cmd, shell=True, check=True)
print("Success!")
