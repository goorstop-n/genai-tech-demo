import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer

# 模型名称，可以修改为你想测试的模型；
model_name = "Qwen/Qwen3-4B-Instruct-2507"

# 加载tokenizer和model；
print(f"<<< 加载tokenizer和model：")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")

# 查看大模型对应的词表有多少个Token？
print(f"<<< 查看大模型对应的词表有多少个Token？")
print(f"大模型{model_name}的词表中有{tokenizer.vocab_size}个token。\n")

# Sample一些Token看下；
print(f"<<< 可以sample一些Token看下；")
print(f"大模型{model_name}的词表中编号 0~50 的token是：")
for token_id in range(0, 50):
    print(tokenizer.decode(token_id, skip_special_tokens=True), end=" ")
print("\n")

# 查看具体文本对应的Token是什么？
print(f"<<< 查看具体文本对应的Token是什么？")
prompt = "世界上最高山峰是哪座？"
tokens = tokenizer.encode(prompt, add_special_tokens=False)
tokens = {token_id: tokenizer.decode(token_id) for token_id in tokens}
print(prompt, "->", tokens, "\n")

# 给定一个输入Prompt，查看模型输出的概率分布；
print(f"<<< 给定一个输入Prompt，查看模型输出的概率分布；")
prompt = "User：世界上最高山峰是哪座？AI："
max_tokens = 50
for i in range(max_tokens):
    print(f"输入：『{repr(prompt)}』-> LLM -> ", end="")

    outputs = model(tokenizer.encode(prompt, return_tensors="pt").to(model.device))
    last_logits = outputs.logits[:, -1, :]
    probabilities = torch.softmax(last_logits, dim=-1)

    top_k = 5
    top_p, top_indices = torch.topk(probabilities, top_k)
    sampled_index = torch.multinomial(top_p.squeeze(0), num_samples=1).item()
    predict_token = tokenizer.decode(top_indices[0][sampled_index].item())
    print(f"『{repr(predict_token)}』")

    result = {}
    for i in range(top_k):
        token_id = top_indices[0][i].item()
        token = tokenizer.decode(token_id)
        probability = top_p[0][i].item()
        result[token] = f"{probability:.2f}"
    print(f"   <<< 这一轮模型预测Top{top_k}的Token是：{repr(result)}")
    prompt += predict_token
print("")

# 引入Chat Template，看看模型的输出效果；
print(f"<<< 引入Chat Template，看看模型的输出效果；")
prompt = "世界上最高山峰是哪座？"
prompt_with_chat_template = "User：" + prompt + "AI："
input_ids = tokenizer.encode(prompt_with_chat_template, return_tensors="pt").to(model.device)
outputs = model.generate(
    input_ids,
    max_length=200,
    do_sample=True,
    top_k=5,
    pad_token_id=tokenizer.eos_token_id,
    attention_mask=torch.ones_like(input_ids)
)
generated_text = tokenizer.decode(outputs[0])
print(f"输入：\n{prompt_with_chat_template}，\n输出：\n{generated_text}\n")

# 使用官方Chat Template看看效果；
print(f"<<< 使用官方Chat Template看看效果；")
prompt = "世界上最高山峰是哪座？"
messages = [
    {"role": "user", "content": prompt},
]
input_ids = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt")["input_ids"].to(model.device)
outputs = model.generate(
    input_ids,
    max_length=1000,
    do_sample=True,
    top_k=5,
    pad_token_id=tokenizer.eos_token_id,
    attention_mask=torch.ones_like(input_ids)
)
generated_text = tokenizer.decode(outputs[0])
print(f"用户输入：\n{prompt}\n"
      f"引入官方Chat Template后的输入：\n{tokenizer.decode(input_ids[0])}"
      f"输出：\n{generated_text}\n")

# 模型如何实现多轮对话；
print(f"<<< 模型如何实现多轮对话？")
prompt = "第二高和第三高呢？"
messages = [
    {"role": "user", "content": "世界上最高山峰是哪座？"},
    {"role": "assistant", "content": "世界上最高的山峰是珠穆朗玛峰。"},
    {"role": "user", "content": prompt},
]
input_ids = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt")["input_ids"].to(model.device)
outputs = model.generate(
    input_ids,
    max_length=1000,
    do_sample=True,
    top_k=5,
    pad_token_id=tokenizer.eos_token_id,
    attention_mask=torch.ones_like(input_ids)
)
generated_text = tokenizer.decode(outputs[0])
print(f"用户输入：\n{prompt}\n"
      f"引入官方Chat Template后的输入：\n{tokenizer.decode(input_ids[0])}"
      f"输出：\n{generated_text}\n")

# 今天是几月几号验证：
print(f"<<< 今天是几月几号验证：")
prompt = "今天是几月几号？"
messages = [
    {"role": "system", "content": "今天是2026年1月1日。"},
    {"role": "user", "content": prompt},
]
input_ids = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt")["input_ids"].to(model.device)
outputs = model.generate(
    input_ids,
    max_length=1000,
    do_sample=True,
    top_k=5,
    pad_token_id=tokenizer.eos_token_id,
    attention_mask=torch.ones_like(input_ids)
)
generated_text = tokenizer.decode(outputs[0])
print(f"用户输入：\n{prompt}\n"
      f"引入官方Chat Template后的输入：\n{tokenizer.decode(input_ids[0])}"
      f"输出：\n{generated_text}\n")

