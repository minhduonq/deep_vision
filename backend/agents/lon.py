# Single image edit

from gradio_client import Client, handle_file

client = Client("multimodalart/Qwen-Image-Edit-Fast")
result = client.predict(
		image=handle_file('https://i.pinimg.com/1200x/ea/32/4a/ea324a057a2fa35f84e76fd126bdbc87.jpg'),
		prompt="Change the color of the sheet to light yellow",
		seed=0,
		randomize_seed=True,
		true_guidance_scale=1,
		num_inference_steps=8,
		rewrite_prompt=True,
		api_name="/infer"
)
print(result)

# Output:
# Loaded as API: https://multimodalart-qwen-image-edit-fast.hf.space ✔
# ('/tmp/gradio/52cd19636a2863435c9dd3a7dc88491b00a950075ef3b6b16cbe76b4bb5a3065/image.webp', 1355813495)

# Multiple image edit

from gradio_client import Client, handle_file

client = Client("prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast-Fusion")
result = client.predict(
	image_1=handle_file('https://prithivmlmods-qwen-image-edit-2509-loras-fast-fusion.hf.space/gradio_api/file=/tmp/gradio/13df97c16d449e4203b4e97d96f269dec67b5971bfcf162d07a6f150b55a9e8e/F3.jpg'),
	image_2=handle_file('https://prithivmlmods-qwen-image-edit-2509-loras-fast-fusion.hf.space/gradio_api/file=/tmp/gradio/c3a84cf04cc7ae78f7acc42ebbc80bee0fcd423642c9f02897a17ad4df1fee7f/F4.jpg'),
	prompt="Replace her glasses with the new glasses from image 1.",
	lora_adapter="Super-Fusion",
	seed=0,
	randomize_seed=True,
	guidance_scale=1,
	steps=4,
	api_name="/infer"
)
print(result)

# Output:
# /usr/local/lib/python3.12/dist-packages/huggingface_hub/utils/_auth.py:94: UserWarning: 
# The secret `HF_TOKEN` does not exist in your Colab secrets.
# To authenticate with the Hugging Face Hub, create a token in your settings tab (https://huggingface.co/settings/tokens), set it as secret in your Google Colab and restart your session.
# You will be able to reuse this secret in all of your notebooks.
# Please note that authentication is recommended but still optional to access public models or datasets.
#   warnings.warn(
# Loaded as API: https://prithivmlmods-qwen-image-edit-2509-loras-fast-fusion.hf.space ✔
# ('/tmp/gradio/189eee75dca4715ca441f923a0ab56d4e6de78e983763630531f6d3a35a16da0/image.png', 785455840)