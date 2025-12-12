from gradio_client import Client, handle_file

# client = Client("Tongyi-MAI/Z-Image-Turbo")
# result = client.predict(
# 	prompt="Create a picture of a futuristic cityscape at sunset.",
# 	resolution="1024x1024 ( 1:1 )",
# 	seed=42,
# 	steps=8,
# 	shift=3,
# 	random_seed=True,
# 	gallery_images=[],
# 	api_name="/generate"
# )
# print(result)

from gradio_client import Client, handle_file

client = Client("Qwen/Qwen-Image-Edit-2509")
result = client.predict(
	images=[handle_file('acd1.jpg')],
	prompt="Hello!!",
	seed=0,
	randomize_seed=True,
	true_guidance_scale=4,
	num_inference_steps=40,
	height=256,
	width=256,
	rewrite_prompt=True,
	api_name="/infer"
)
print(result)