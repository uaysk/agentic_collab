from pydantic import BaseModel
import traceback
from typing import Any
import datetime
from utils import debug
from ..common import openai_config, get_prompt_file_path
from ..gpt_structure import safe_generate_structured_response
from ..print_prompt import print_run_prompts
from persona.prompt_template.gpt_structure import ChatGPT_single_request, get_embedding
from persona.cognitive_modules.retrieve import new_retrieve

import json
from pathlib import Path
import time
import traceback
from openai import AzureOpenAI, OpenAI
from utils import openai_api_key, use_openai, api_model
from openai_cost_logger import DEFAULT_LOG_PATH
from persona.prompt_template.openai_logger_singleton import OpenAICostLogger_Singleton

def create_prompt(prompt_input: dict[str, Any]):
  identity_stable_set = prompt_input["identity_stable_set"]
  lifestyle = prompt_input["lifestyle"]
  curr_date = prompt_input["curr_date"]
  persona_name = prompt_input["persona_name"]
  wake_up_hour = prompt_input["wake_up_hour"]

  prompt = f"""
{identity_stable_set}

In general, {lifestyle}
Today is {curr_date}. Describe {persona_name}'s plan for the whole day, from morning 'til night, in broad-strokes. Include the time of the day. e.g., "wake up and complete their morning routine at {wake_up_hour}", "have lunch at 12:00 pm", "watch TV from 7 to 8 pm".
"""
  return prompt

class DailyPlan(BaseModel):
  daily_plan: list[str]

config_path = Path("../../openai_config.json")
with open(config_path, "r") as f:
  openai_config = json.load(f) 

client = OpenAI(api_key=openai_api_key)

def temp_sleep(seconds=0.1):
  time.sleep(seconds)

def ChatGPT_single_request_2(prompt):
  temp_sleep()

  print("--- ChatGPT_single_request() ---")
  print("Prompt:", prompt, flush=True)

  completion = client.chat.completions.create(
    model=openai_config["model"],
    messages=[{"role": "user", "content": prompt}],
  )

  content = completion.choices[0].message.content
  print("Response content:", content, flush=True)

  if content:
    content = content.strip("`").removeprefix("json").strip()
    return content
  else:
    print("Error: No message content from LLM.", flush=True)
    return ""
  
def revise_identity_2(persona): 
  p_name = persona.scratch.name

  focal_points = [f"{p_name}'s plan for {persona.scratch.get_str_curr_date_str()}.",
                  f"Important recent events for {p_name}'s life."]
  retrieved = new_retrieve(persona, focal_points)

  statements = "[Statements]\n"
  for key, val in retrieved.items():
    for i in val: 
      statements += f"{i.created.strftime('%A %B %d -- %H:%M %p')}: {i.embedding_key}\n"

  # print (";adjhfno;asdjao;idfjo;af", p_name)
  plan_prompt = statements + "\n"
  plan_prompt += f"Given the statements above, is there anything that {p_name} should remember as they plan for"
  plan_prompt += f" *{persona.scratch.curr_time.strftime('%A %B %d')}*? "
  plan_prompt += f"If there is any scheduling information, be as specific as possible (include date, time, and location if stated in the statement)\n\n"
  plan_prompt += f"Write the response from {p_name}'s perspective."
  plan_note = ChatGPT_single_request_2(plan_prompt)
  # print (plan_note)

  thought_prompt = statements + "\n"
  thought_prompt += f"Given the statements above, how might we summarize {p_name}'s feelings about their days up to now?\n\n"
  thought_prompt += f"Write the response from {p_name}'s perspective."
  thought_note = ChatGPT_single_request_2(thought_prompt)
  # print (thought_note)

  currently_prompt = f"{p_name}'s status from {(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')}:\n"
  currently_prompt += f"{persona.scratch.currently}\n\n"
  currently_prompt += f"{p_name}'s thoughts at the end of {(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')}:\n" 
  currently_prompt += (plan_note + thought_note).replace('\n', '') + "\n\n"
  currently_prompt += f"It is now {persona.scratch.curr_time.strftime('%A %B %d')}. Given the above, write {p_name}'s status for {persona.scratch.curr_time.strftime('%A %B %d')} that reflects {p_name}'s thoughts at the end of {(persona.scratch.curr_time - datetime.timedelta(days=1)).strftime('%A %B %d')}. Write this in third-person talking about {p_name}."
  currently_prompt += f"If there is any scheduling information, be as specific as possible (include date, time, and location if stated in the statement).\n\n"
  currently_prompt += "Follow this format below:\nStatus: <new status>"
  # print ("DEBUG ;adjhfno;asdjao;asdfsidfjo;af", p_name)
  # print (currently_prompt)
  new_currently = ChatGPT_single_request_2(currently_prompt)
  # print (new_currently)
  # print (new_currently[10:])

  persona.scratch.currently = new_currently

  daily_req_prompt = persona.scratch.get_str_iss() + "\n"
  daily_req_prompt += f"Today is {persona.scratch.curr_time.strftime('%A %B %d')}. Here is {persona.scratch.name}'s plan today in broad-strokes (with the time of the day. e.g., have a lunch at 12:00 pm, watch TV from 7 to 8 pm).\n\n"
  daily_req_prompt += f"Follow this format (the list should have 4~6 items but no more):\n"
  daily_req_prompt += f"1. wake up and complete the morning routine at <time>, 2. ..."

  new_daily_req = ChatGPT_single_request_2(daily_req_prompt)
  new_daily_req = new_daily_req.replace('\n', ' ')
  print ("DEBUG new_daily_req:", new_daily_req)
  persona.scratch.daily_plan_req = new_daily_req

def run_gpt_prompt_daily_plan(persona, wake_up_hour, test_input=None, verbose=False):
  """
  Basically the long term planning that spans a day. Returns a list of actions
  that the persona will take today. Usually comes in the following form:
  'wake up and complete the morning routine at 6:00 am',
  'eat breakfast at 7:00 am',..
  Note that the actions come without a period.

  INPUT:
    persona: The Persona class instance
  OUTPUT:
    a list of daily actions in broad strokes.
  """

  def create_prompt_input(persona, wake_up_hour, test_input=None):
    if test_input:
      return test_input

    ## Triggering Identity revision at the star of the first day
    if persona.scratch.get_str_curr_date_str() is None:
       revise_identity_2(persona)

    prompt_input = {
      "identity_stable_set": persona.scratch.get_str_iss(),
      "lifestyle": persona.scratch.get_str_lifestyle(),
      "curr_date": persona.scratch.get_str_curr_date_str(),
      "persona_name": persona.scratch.get_str_firstname(),
      "wake_up_hour": f"{str(wake_up_hour)}:00",
    }

    return prompt_input

  def __func_clean_up(gpt_response, prompt=""):
    return gpt_response.daily_plan

  def __func_validate(gpt_response, prompt=""):
    try:
      __func_clean_up(gpt_response, prompt="")
    except Exception:
      traceback.print_exc()
      return False
    return True

  def get_fail_safe():
    fs = [
      "wake up and complete the morning routine at 6:00 am",
      "eat breakfast at 7:00 am",
      "read a book from 8:00 am to 12:00 pm",
      "have lunch at 12:00 pm",
      "take a nap from 1:00 pm to 4:00 pm",
      "relax and watch TV from 7:00 pm to 8:00 pm",
      "go to bed at 11:00 pm",
    ]
    return fs

  gpt_param = {
    "engine": openai_config["model"],
    "max_tokens": 2000,
    "temperature": 1,
    "top_p": 1,
    "stream": False,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "stop": None,
  }
  prompt_file = get_prompt_file_path(__file__)
  prompt_input = create_prompt_input(persona, wake_up_hour, test_input)
  prompt = create_prompt(prompt_input)
  fail_safe = get_fail_safe()

  output = safe_generate_structured_response(
    prompt, gpt_param, DailyPlan, 5, fail_safe, __func_validate, __func_clean_up
  )

  if debug or verbose:
    print_run_prompts(prompt_file, persona, gpt_param, prompt_input, prompt, output)

  return output, [output, prompt, gpt_param, prompt_input, fail_safe]
