from llama_cpp import Llama
import json
import sys
import pprint
import handlers
from llama_cpp.llama_tokenizer import LlamaHFTokenizer

pp = pprint.PrettyPrinter(indent=2)


class Assistant:
    def __init__(self, init_context):
        json_text = open("functions.json", "r").read()

        self.functions = json.loads(json_text)

        self.llm = Llama(
            model_path="models/functionary-small-v2.4.Q4_0.gguf",
            n_ctx=4096,
            n_gpu_layers=35,
            chat_format="functionary-v2",
            tokenizer=LlamaHFTokenizer.from_pretrained(
                "meetkai/functionary-small-v2.4-GGUF"),
            verbose=True)

        self.function_calls = {}
        self.init_context = init_context

        self.init()

    def init(self):
        self.messages = self.init_context.copy()

    def run_inference(self):
        all_messages = list(self.messages)

        result = self.llm.create_chat_completion(
            messages=all_messages,
            tools=self.functions,
            tool_choice="auto",
        )

        print(result['choices'][0]['message'])

        return result['choices'][0]['message']

    def confirm(self, func_id, data=""):
        func_call = self.function_calls[func_id]
        func_name = func_call["function"]["name"]
        func_param = func_call["function"]["arguments"]

        result = None

        match func_name:
            case 'get_all_projects':
                result = handlers.get_all_projects()
            case 'get_projects_for_user':
                result = handlers.get_projects_for_user(func_param)
            case 'create_project':
                result = handlers.create_project(func_param)
            case 'get_all_employees':
                result = handlers.get_all_employees()
            case 'add_employee':
                result = handlers.add_employee(func_param)
            case 'assign_project_to_employee':
                result = handlers.assign_project_to_employee(func_param)
            case 'add_activities':
                result = handlers.add_activities(func_param)
            case 'get_project_activities':
                result = handlers.get_project_activities(func_param)
            case 'add_absence':
                result = handlers.add_absence(func_param)
            case 'prompt_date':
                result = data

        # self.messages.append(
        #     {"role": "tool", "tool_call_id": func_id, "name": func_name, "content": result})
        self.messages.append({"role": "function", "tool_call_id": func_id, "name": func_name, "content": str(result)})

        del self.function_calls[func_id]

    def generate_message(self, send_client_callback, user_input=None):
        if user_input is not None:
            self.messages.append({"role": "user", "content": user_input})

        pp.pprint(self.messages)

        inference = self.run_inference()

        print("***Inference", inference)
        pp.pprint(self.messages)

        tool_calls = inference['tool_calls']

        if tool_calls:
            for tool_call in tool_calls:
                tool_id = tool_call["id"]
                self.function_calls[tool_id] = tool_call
                func_name = tool_call["function"]["name"]

                # Auto validate all get functions
                if "get" in func_name:
                    print("Autovalidating message")
                    self.confirm(tool_id)
                    self.generate_message(send_client_callback)
                else:
                    print("Message needs validation")
                    send_client_callback(
                        {"role": "system-confirm", "content": inference["content"], "function": tool_call["function"],
                         "tool_id": tool_id})
        else:
            print("No tool calls")
            send_client_callback(inference)

        self.messages.append(inference)
