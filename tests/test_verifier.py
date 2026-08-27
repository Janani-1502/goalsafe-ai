from hazard_verifier import assess_image

IMAGE_PATH = "05_fire_hazard.png"

with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

print("Running GoalSafe verifier...")

result, decision = assess_image(
    image_bytes,
    "Check whether is any fire hazard"
)

print("\n--- MODEL FIELDS ---")
print("goal_match:", result.goal_match)
print("condition:", result.condition)
print("condition_description:", result.condition_description)
print("evidence_sufficient:", result.evidence_sufficient)
print("goal_relevant_fact:", result.goal_relevant_fact)
print("observed_facts:", result.observed_facts)
print("spatial_relationships:", result.spatial_relationships)
print("decision:", decision)