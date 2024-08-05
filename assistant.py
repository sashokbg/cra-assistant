import pprint
import json

from openai import OpenAI

import handlers

pp = pprint.PrettyPrinter(indent=2)


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


class Assistant:
    def __init__(self, init_context):
        # self.client = OpenAI(base_url="http://localhost:8000/v1", api_key="sk-xxx")
        self.client = OpenAI()

        json_text = open("functions.json", "r").read()

        self.functions = json.loads(json_text)
        self.function_calls = {}
        self.init_context = init_context

        self.init()

    def init(self):
        self.messages = self.init_context.copy()

    def run_inference(self):
        all_messages = list(self.messages)

        result = self.client.chat.completions.create(
            messages=all_messages,
            model="gpt-4o",
            tools=self.functions,
            tool_choice="auto",
        )

        return result.choices[0].message

    def confirm(self, func_id, data=""):
        func_call = self.function_calls[func_id]
        func_name = func_call.function.name
        func_param = func_call.function.arguments

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
        self.messages.append({
            "role": "tool",
            "tool_call_id": func_id,
            "name": func_name,
            "content": str(result)})

        del self.function_calls[func_id]

    def generate_message(self, send_client_callback, user_input=None):
        if user_input is not None:
            self.messages.append({"role": "user", "content": user_input})

        pp.pprint(self.messages)

        message = self.run_inference()

        print("***Inference", message)

        tool_calls = None

        if message.tool_calls and len(message.tool_calls) > 0:
            tool_calls = message.tool_calls

        if tool_calls:
            for tool_call in tool_calls:
                tool_id = tool_call.id
                self.function_calls[tool_id] = tool_call
                func_name = tool_call.function.name

                # Auto validate all get functions
                if "get" in func_name:
                    print("Autovalidating message")
                    self.messages.append(get_json(message))
                    self.confirm(tool_id)
                    self.generate_message(send_client_callback)
                else:
                    print("Message needs validation")
                    send_client_callback(
                        {"role": "system-confirm",
                         "content": message.content,
                         "function": {"name": tool_call.function.name,
                                      "arguments": tool_call.function.arguments},
                         "tool_id": tool_id}
                    )
                    self.messages.append(get_json(message))
        else:
            print("No tool calls")
            inference_to_json = {"role": "assistant", "content": message.content}
            if inference_to_json:
                self.messages.append(inference_to_json)
            send_client_callback(
                inference_to_json
            )
