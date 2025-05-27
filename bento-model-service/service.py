import bentoml
from transformers import AutoTokenizer, AutoModelForCausalLM
from bentoml.io import JSON
from pydantic import BaseModel
import torch

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 128

@bentoml.service(resources={"cpu": "1"}) 
class GenerationService:
    def __init__(self):
        self.model_id = "EleutherAI/gpt-neo-1.3B"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id)

    @bentoml.api()
    def generate(self, body: GenerateRequest):
        inputs = self.tokenizer(body.prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=body.max_tokens,
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"response": text}
