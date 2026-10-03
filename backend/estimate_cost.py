'''
Populate `s` in main with logs/terminal outputs with 
verbose=True for LLMs for LLM cost estimate.

Estimate based on the pricing here: https://cloud.google.com/vertex-ai/generative-ai/pricing
'''

def run_estimate(s: str):

    lines = s.split('\n')

    num_llm_calls = 0
    gemini_1_5_pro_cost, gemini_1_0_pro_cost, gemini_1_5_flash_cost = 0, 0, 0
    total_input_cost, total_output_cost, total_cost = 0, 0, 0
    for i in range(len(lines)-2):
    
        model_line = lines[i]
        input_line = lines[i+1]
        output_line = lines[i+2]
    
        if model_line == '[GEMINI-1.5-PRO]':
            num_llm_calls += 1
            input_characters = int(input_line[7:-12].strip())
            output_characters = int(output_line[8:-12].strip())
            input_cost = 0.0003125*input_characters/1000 if input_characters < 128000*4 else 0.000625*input_characters/1000
            output_cost = 0.00125*output_characters/1000 if input_characters < 128000*4 else 0.0025*output_characters/1000
            total_input_cost += input_cost
            total_output_cost += output_cost
            total_cost += input_cost + output_cost
            gemini_1_5_pro_cost += input_cost + output_cost
        elif model_line == '[GEMINI-1.0-PRO]':
            num_llm_calls += 1
            input_characters = int(input_line[7:-12].strip())
            output_characters = int(output_line[8:-12].strip())
            input_cost = 0.000125*input_characters/1000
            output_cost = 0.000375*output_characters/1000
            total_input_cost += input_cost
            total_output_cost += output_cost
            total_cost += input_cost + output_cost
            gemini_1_0_pro_cost += input_cost + output_cost
        elif model_line == '[GEMINI-1.5-FLASH]':
            num_llm_calls += 1
            input_characters = int(input_line[7:-12].strip())
            output_characters = int(output_line[8:-12].strip())
            input_cost = 0.00001875*input_characters/1000 if input_characters < 128000*4 else 0.0000375*input_characters/1000
            output_cost = 0.000075*output_characters/1000 if input_characters < 128000*4 else 0.00015*output_characters/1000
            total_input_cost += input_cost
            total_output_cost += output_cost
            total_cost += input_cost + output_cost
            gemini_1_5_flash_cost += input_cost + output_cost
    
    print()
    print("{} LLM CALL(S).".format(num_llm_calls))
    print()
    print("GEMINI 1.5 PRO COST: ${}".format(gemini_1_5_pro_cost))
    print("GEMINI 1.5 FLASH COST: ${}".format(gemini_1_5_flash_cost))
    print("GEMINI 1.0 PRO COST: ${}".format(gemini_1_0_pro_cost))
    print()
    print("TOTAL INPUT COST: ${}".format(total_input_cost))
    print("TOTAL OUTPUT COST: ${}".format(total_output_cost))
    print("TOTAL COST: ${}".format(total_cost))
    print()

if __name__ == "__main__":
    s = """
[GEMINI-1.5-PRO]
INPUT: 18851 CHARACTERS.
OUTPUT: 4079 CHARACTERS.
[GEMINI-1.5-FLASH]
INPUT: 18851 CHARACTERS.
OUTPUT: 4079 CHARACTERS.
[GEMINI-1.0-PRO]
INPUT: 18851 CHARACTERS.
OUTPUT: 4079 CHARACTERS.
"""
    run_estimate(s)