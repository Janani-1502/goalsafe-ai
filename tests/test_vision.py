import ollama

IMAGE_PATH = r"2_wet_floor_slip_hazard.png"

with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

print("Sending image to Gemma...")

response = ollama.chat(
    model="gemma3:4b",
    messages=[
        {
            "role": "user",
            "content": "Describe this image and identify any visible safety hazard.",
            "images": [image_bytes],
        }
    ],
)

print("\nMODEL RESPONSE:")
print(response["message"]["content"])