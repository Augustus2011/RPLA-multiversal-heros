
import os
from tools import o3_mini,gemini2_flash_thinking,gemini2_flash

# print(sonnet_37("what is the result of 1+3 ?"))
# print(deepseek_v3("what is the result of 1+3 ?"))
print(gemini2_flash_thinking(input_prompt="hello who are you, I am under the water pls help me"))
print(gemini2_flash(input_prompt="hello who are you, I am under the water pls help me"))
# print(gemini2_flash_thinking("what is the result of 1+3 ?"))
# print(r1("what is the result of 1+3 ?"))

