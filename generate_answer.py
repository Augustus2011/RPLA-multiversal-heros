import argparse
import pandas as pd
import json
import os
import time
from tools import gemini2_flash_thinking,deepseek_v3,sonnet_37,r1, r1_zero,o3_mini,gemini2_flash,gemini_j,initialize_vertexai
import re

from ast import literal_eval


initialize_vertexai()
def get_model(model_name):
    models = {"gemini2-thinking": gemini2_flash_thinking,"gemini2":gemini2_flash, "r1": r1, "r1_zero": r1_zero,"o3":o3_mini,"v3":deepseek_v3,"37":sonnet_37}
    return models.get(model_name, None)

def dilemma_answer(df, model, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            cid = row["CID"]
            name = row["Name"]
            des = row["Description (only from pdb)"]
            lore = "".join([k for k in row["Source"]])
            print(f"Processing: {name} (CID: {cid})")
            dilemma1=row["Dilemma(1) Save vs. Sacrifice (Personal Sacrifice vs. Greater Good)"]
            dilemma2=row["Dilemma (2) Hero or Villain (Morality and Identity Crisis)"]
            dilemma3=row["Dilemma(3) Duty vs. Personal Desire"]
            dilemma4=row["Dilemma(4) The Ends Justify the Means vs. Moral Code"]
            d_detail=""
            for num, dilemma in enumerate([dilemma1,dilemma2,dilemma3,dilemma4]):
                if num==0:
                    d_detail="What will you choese between A) save(personal sacrifice) vs B) sacrifice(greater good)"
                elif num==1:
                    d_detail="About morality and identity crisis,what will you choese between A) Hero vs B) Villain"
                elif num==2:
                    d_detail="what will you choese between A) Duty vs. B) Personal Desire"
                elif num==3:
                    d_detail="what will you choese between A) The Ends Justify the Means vs. B) Moral Code"
                    
                input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}, the situation is {dilemma}\n <question> {d_detail} <question/>"


                try:
                    time.sleep(3)
                    answer = model(input_prompt=input_prompt)
                    time.sleep(3)
                    print(f"Response {num}: {answer[:100]}...")
                except Exception as e:
                    print(f"Error for CID {cid}: {e}")
                    answer = f"Error: {str(e)}"
                json_obj = {"CID": cid, "name": name, "lore": lore, "answers": answer,"question":dilemma}
                f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")

def character_knowledge(df, model, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            cid = row["CID"]
            name = row["Name"]
            des = row["Description (only from pdb)"]
            lore = "".join([k for k in row["Source"]])
            print(f"Processing: {name} (CID: {cid})")
            input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}\n <question> describe what you know about yourself <question/>"

            try:
                time.sleep(3)
                answer = model(input_prompt=input_prompt)
                time.sleep(3)
                print(f"Response {_}: {answer[:100]}...")
            except Exception as e:
                print(f"Error for CID {cid}: {e}")
                answer = f"Error: {str(e)}"
            json_obj = {"CID": cid, "name": name, "lore": lore, "answers": answer}
            f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")

def canon_event(df, model, output_path,cot:bool=False):

    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            cid = row["CID"]
            name = row["Name"]
            des = row["Description (only from pdb)"]
            lore = "".join([k for k in row["Source"]])
            true_label = row['True event'].split(" ")
            print(f"Processing: {name} (CID: {cid})")
            for q_i, question in enumerate(row.iloc[6:12]):
                if isinstance(question, str):
                    input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}\n <question> {question} <question/>"
                    if cot:
                        #zero-shot CoT
                        input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}\n <question> {question} , Let's think step by step.<question/>"

                #     input_prompt=f"""following this instruction think inside <think> \n answer in tag <answer> \n 
                # example input question : what is the result of 1+3 ?
                # <think> integer number 1 plus integer number 3 is equal to 4, i must answer as 4</think> 
                # <answer>4<answer/> 
                # \n real question: you are {name},act and think as {name}, {des} from {lore},question: {question} and must give the one answer A, B, C or D"""
                
                    try:
                        time.sleep(3)
                        answer = model(input_prompt=input_prompt)
                        time.sleep(3)
                        print(f"Response {_}: {answer[:100]}...")
                    except Exception as e:
                        print(f"Error for CID {cid}: {e}")
                        answer = f"Error: {str(e)}"
                    json_obj = {"CID": cid, "name": name, "lore": lore, "answers": answer, "question": question, "true_label": true_label[q_i]}
                    f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")

    
    df=pd.read_csv("./all_character_data-canon.csv")

    with open(f"{output_path}", "r") as f:
            data = f.readlines()


    file_name=os.path.basename(output_path).split(".")[0]

    predicted_l=[]
    gt_l=[]
    c=0
    for i,row in df.iterrows():#data_df.iterrows():
        cid=row["CID"]
        true_answers=row["True event"]
        
        print(cid)
        # print(c)
        for answer in true_answers.split(" "):

            #print(answer)
            gt_l.append(answer)
            time.sleep(0.2)
            
            if answer not in ["B","A","C","D"]:
                predicted_l.append("_")
            else:
                d=literal_eval(data[c])

                if answer not in ["A","B","C","D"]:
                    predicted_l.append("_")
                    c+=1
                else:
                    predicted=d["answers"]
                    c+=1
                    
                    answer_letter=gemini_j(text=f"you are must capture only one true answer return A or B or C or D \n here the input:{predicted}").strip()
                    if answer_letter not in ["A","B","C","D"]:
                        predicted_l.append("O")
                    else:
                        predicted_l.append(answer_letter)



        from sklearn.metrics import accuracy_score



        gt_l_child     = [gt_l[i] for i in range(len(gt_l)) if i % 6 == 0]
        pred_l_child   = [predicted_l[i] for i in range(len(predicted_l)) if i % 6 == 0]
        gt_l_child     = [label for label in gt_l_child if label != '_']
        pred_l_child   = [label for label in pred_l_child if label != '_']


        gt_l_teen      = [gt_l[i] for i in range(len(gt_l)) if i % 6 == 1]
        pred_l_teen    = [predicted_l[i] for i in range(len(predicted_l)) if i % 6 == 1]
        gt_l_teen     = [label for label in gt_l_teen if label != '_']
        pred_l_teen   = [label for label in pred_l_teen if label != '_']

        gt_l_pre       = [gt_l[i] for i in range(len(gt_l)) if i % 6 == 2]
        pred_l_pre     = [predicted_l[i] for i in range(len(predicted_l)) if i % 6 == 2]
        gt_l_pre     = [label for label in gt_l_pre if label != '_']
        pred_l_pre   = [label for label in pred_l_pre if label != '_']

        gt_l_hero123   = [gt_l[i] for i in range(len(gt_l)) if i % 6 in [3, 4, 5]]
        pred_l_hero123 = [predicted_l[i] for i in range(len(predicted_l)) if i % 6 in [3, 4, 5]]
        gt_l_hero123   = [label for label in gt_l_hero123 if label != '_']
        pred_l_hero123 = [label for label in pred_l_hero123 if label != '_']


        gt_l_ = [label for label in gt_l if label != '_']
        predicted_l_ = [label for label in predicted_l if label != '_']

        # Compute accuracy
        acc_all     = accuracy_score(gt_l_, predicted_l_)
        acc_child   = accuracy_score(gt_l_child, pred_l_child)
        acc_teen    = accuracy_score(gt_l_teen, pred_l_teen)
        acc_pre     = accuracy_score(gt_l_pre, pred_l_pre)
        acc_hero123 = accuracy_score(gt_l_hero123, pred_l_hero123)

        # Save results
        df_result = pd.DataFrame([{
            "model": file_name,
            "acc_child": acc_child,
            "acc_teen": acc_teen,
            "acc_pre": acc_pre,
            "acc_hero123": acc_hero123,
            "acc_all": acc_all,
        }])

        df_result.to_csv(f"{file_name}.csv", index=False)


def get_quote(df, model, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            cid = row["CID"]
            name = row["Name"]
            des = row["Description (only from pdb)"]
            lore = "".join([k for k in row["Source"]])
            print(f"Processing: {name} (CID: {cid})")
            input_prompt = f"""You are {name}, act and think as {name}, {des} from {lore}\n <question> say the "catchphrase" or "iconic quote."<question/>"""
            
            try:
                time.sleep(3)
                answer = model(input_prompt=input_prompt)
                time.sleep(3)
                print(f"Response {_}: {answer[:100]}...")
            except Exception as e:
                print(f"Error for CID {cid}: {e}")
                answer = f"Error: {str(e)}"
            json_obj = {"CID": cid, "name": name, "lore": lore, "answers": answer}
            f.write(json.dumps(json_obj, ensure_ascii=False) + "\n")



def reprocess_failed_results(input_file, output_file,model,task):
    df=pd.read_csv("all_character_data.csv")
    c=0
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
            for num_line,line in enumerate(infile):
                data = json.loads(line)
                if re.search(r'Error: API|Error: 429|Error:|Error: 503', data['answers']):
                    cid = data["CID"]
                    name = data["name"]
                    lore = data["lore"]
                    des =df[df["CID"]==cid].iloc[0,5]
                    print(f"Reprocessing: {name} (CID: {cid})")
                    
                    if task =="dilemma":
                        dilemma = data["question"]
                        # input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}, the situation is {dilemma}"
                        if num_line%4==0:
                            d_detail="What will you choese between A) save(personal sacrifice) vs B) sacrifice(greater good)"
                        elif num_line%4==1:
                            d_detail="About morality and identity crisis,what will you choese between A) Hero vs B) Villain"
                        elif num_line%4==2:
                            d_detail="what will you choese between A) Duty vs. B) Personal Desire"
                        elif num_line%4==3:
                            d_detail="what will you choese between A) The Ends Justify the Means vs. B) Moral Code"
                            
                        input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}, the situation is {dilemma}\n <question> {d_detail} <question/>"
                        # input_prompt=f"""following this instruction think inside <think> \n answer in tag <answer> \n 
                        # example input question : what is the result of 1+3 ?
                        # <think> integer number 1 plus integer number 3 is equal to 4, i must answer as 4</think> 
                        # <answer>4<answer/> 
                        # \n real question: you are {name},act and think as {name}, {des} from {lore},the situation is {dilemma},{d_detail}"""
                    
                    elif task=="knowledge":
                        lore=data["lore"]
                        input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}\n <question> describe what you know about yourself <question/>"
                        # input_prompt=f"""following this instruction think inside <think> \n answer in tag <answer> \n 
                        # example input question : what is the result of 1+3 ?
                        # <think> integer number 1 plus integer number 3 is equal to 4, i must answer as 4</think> 
                        # <answer>4<answer/> 
                        # \n real question: you are {name},act and think as {name}, {des} from {lore}, describe yourself"""
                    
                    elif task=="canon":
                        question=data["question"]
                        lore=data["lore"]
                        input_prompt = f"You are {name}, act and think as {name}, {des} from {lore}\n <question> {question} <question/>"
                        # input_prompt=f"""following this instruction think inside <think> \n answer in tag <answer> \n 
                        # example input question : what is the result of 1+3 ?
                        # <think> integer number 1 plus integer number 3 is equal to 4, i must answer as 4</think> 
                        # <answer>4<answer/>
                        # \n real question: you are {name},act and think as {name}, {des} from {lore},question: {question} and must give the one answer A, B, C or D"""
                        
                    elif task=="quote":
                        lore=data["lore"]
                        input_prompt = f"""You are {name}, act and think as {name}, {des} from {lore}\n <question> say your "catchphrase" or "iconic quote" and give me a short answer, please"<question/>"""
                        
                    answer = model(input_prompt)
                    print(f"Updated response: {answer[:100]}...")
                    data["answers"] = answer
                    outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
            
                else:
                    outfile.write(line)
                c+=1
def main():
    parser = argparse.ArgumentParser(description="Process character data using different AI models.")
    parser.add_argument("--model", choices=["gemini2","gemini2-thinking", "r1", "r1_zero","o3","v3","37"], required=True, help="Select model: gemini2, r1,r1_zero or o3")
    parser.add_argument("--csv", required=True,default="all_character_data-canon.csv", help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to save JSONL output")
    parser.add_argument("--task", choices=["dilemma", "knowledge", "canon","quote"], required=True, help="Select task type ex dilemma, knowledge, canon and quote")
    parser.add_argument("--apierror", action="store_true", help="Select retry run with same API")
    parser.add_argument("--inputfile", required=False, help="Select file to reprocess must be jsonl")
    parser.add_argument("--cot", action="store_true", help="Select use CoT")
    args = parser.parse_args()
    
    model = get_model(args.model)
    if model is None:
        print("Invalid model selection.")
        return
    
    df = pd.read_csv(args.csv)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    if args.task == "dilemma" and args.apierror==False:
        dilemma_answer(df, model, args.output)
    elif args.task == "knowledge" and args.apierror==False:
        character_knowledge(df, model, args.output)
    elif args.task == "canon" and args.apierror==False:
        canon_event(df, model, args.output,cot=args.cot)
    elif args.task == "quote" and args.apierror==False:
        get_quote(df,model,args.output)
    elif args.apierror==True and args.inputfile:
        reprocess_failed_results(args.inputfile,args.output,model,args.task)


if __name__ == "__main__":
    main()

#python generate_answer.py --model r1 --csv all_character_data.csv --output ./generated_results/r1/canon_r1_rep2.jsonl --task canon 
#python generate_answer.py --model gemini2_flash_thinking --csv all_character_data.csv --output ./generated_results/gemini2/dilemma_gemini2_flash_thinking_rep1.jsonl --task dilemma
#python generate_answer.py --model r1_zero --csv all_character_data.csv --output ./generated_results/r1_zero/dilemma_r1_zero_rep1_fixed.jsonl --task dilemma --apierror True --inputfile ./generated_results/r1_zero/dilemma_r1_zero_rep1.jsonl
#python generate_answer.py --model r1 --csv all_character_data.csv --output ./generated_results/r1/cannon_r1_rep1_fixed.jsonl --task cannon --apierror True --inputfile ./generated_results/r1/cannon_r1_rep1.jsonl

#python generate_answer.py --model o3_mini --csv all_character_data.csv --output ./generated_results/o3/canon_o3_mini_rep1.jsonl --task canon
#python generate_answer.py --model o3_mini --csv all_character_data.csv --output ./generated_results/o3/dilemma_o3_mini_rep1.jsonl --task dilemma
#python generate_answer.py --model o3_mini --csv all_character_data.csv --output ./generated_results/o3/knowledge_o3_mini_rep1.jsonl --task knowledge
#python generate_answer.py --model gemini2 --csv all_character_data.csv --output ./generated_results/gemini2/dilemma_gemini2_rep1.jsonl --task dilemma


#python generate_answer.py --model r1 --csv all_character_data.csv --output ./generated_results/r1/cannon_r1_rep2_fixed.jsonl --task canon --apierror --inputfile ./generated_results/r1/cannon_r1_rep2.jsonl