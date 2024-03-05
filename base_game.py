import json
from pathlib import Path
from chat import Chat
import random

DATA_PATH = "stark2.txt"

with open(DATA_PATH, 'r', encoding="utf-8") as file:
    events = file.readlines()
TOTAL_EVENTS = len(events)
GAP = 1


def generate_context(beg, end, include_id=False):
    content = ""
    if include_id:
        for i in range(beg, end + 1):
            content += f"id{i}: {events[i]}\n"
        return content
    return '\n'.join(events[beg: end + 1])


class Game:
    def __init__(self, debug=False):
        self.debug = debug
        self.current_event_id = 0
        self.chat = Chat(debug)
        self.chosen_event_plot = ""
        self.changes_to_plot = ""
        self.total_events = TOTAL_EVENTS
        self.achievements = [
            {
                "id": 1,
                "name": "The Direwolf Pact",
                "description": "Ensure Sansa's direwolf, Lady, is not executed.",
                "accomplished": False
            },
            {
                "id": 2,
                "name": "Crowned Stag",
                "description": "Prevent the death of King Robert Baratheon.",
                "accomplished": False
            },
            {
                "id": 3,
                "name": "Honor Preserved",
                "description": "Save Ned Stark from being arrested.",
                "accomplished": False
            },
            {
                "id": 4,
                "name": "Wolf and Lion Dance",
                "description": "Forge an unlikely alliance between House Stark and House Lannister.",
                "accomplished": False
            },
            {
                "id": 5,
                "name": "Keeper of Secrets",
                "description": "Learn all the secrets Jon Arryn uncovered before his death.",
                "accomplished": False
            },
            {
                "id": 6,
                "name": "Quantum Leap",
                "description": "Make a decision that drastically alters the timeline of events from the book.",
                "accomplished": False
            },
            {
                "id": 7,
                "name": "A Song Unchanged",
                "description": "Complete the game without causing any major deviations from the book's main plotline.",
                "accomplished": False
            }
        ]

    def generate_background_summery(self, beg, end):
        prompt = (f"SYSTEM: In the original timeline:*** {generate_context(beg, end)}*** "
                  f"What happens in our new world?"
                  f"Omit all time information in these events."
                  f"Consider these questions when formulating your plot:"
                  f"1. What did astarion do in the past? unless mentioned, he does NOT alter the plot.\n"
                  f"2. Are the people in these events directly affected by past actions of astarion?\n"
                  f"3. If they are directly influenced by astarion, how might they act in the events?\n"
                  f"Summarize the plot (unchanged or adapted) in a concise paragraph.\n"
                  f"Your 50 word paragraph:")

        beck_ground_summery = self.chat.send_message(prompt, keep_in_history=False) + '\n\n'
        # if self.debug:
        #     print(f"generating background_summery for id{beg, end}\nsummery:{beck_ground_summery}\n\n")
        return beck_ground_summery

    def generate_new_event(self, end):
        if self.debug:
            print(f"\ngenerating new event for id{end}, which is {events[end]}\n\n")
        prompt = (f"SYSTEM: Adapt the plot: \"{events[end]}\" to an event in our game world version of ASOIAF universe."
                  f"Account for Astarion's actions in the past, if any."
                  f"Make minimal changes to the original plot, unless Astarion has made a significant change in the past."
                  f"Detail how this event unfolds without presenting the outcome, emphasizing ser Astarion's role."
                  f"prompt the user(who is acting as Astarion) to make a decision based on the event."
                  f"You should ask the player ***What is your choice?*** and provide 2 possible choices starting with 1. and 2.(do not reveal the outcome of the choices)"
                  f"Your 50 word paragraph elaborating on the event's unfold:")
        # self
        return self.chat.send_message(prompt, keep_in_history=False) + '\n\n\n'

    def action_evaluator(self, user_input: str):
        """
        Evaluates the User's action
        :param user_input:
        :return:
        """
        prompt = (f"SYSTEM: Here is the current event: ***{self.chosen_event_plot}***"
                  f"The user made a action of ***{user_input}***"
                  f"You should parse the user action into attempts."
                  f"e.g. user says ***I want to kill Cersi*** parse it into *** Astarion attempts to kill Cersi."
                  f"do not make any explanation"
                  f"Do not change the users action, only output the parsed action."
                  f"briefly output Astarion's (attempted) action:")
        prompt = (
            f"SYSTEM: You are presented with a current event scenario: ***{self.chosen_event_plot}***. "
            f"In response, the user has initiated an action: ***{user_input}***. "
            "Your task is to interpret the user's action as specific attempts within the scenario. "
            "For example, if the user says ***I want to kill Cersei***, you should parse and rephrase it as ***Astarion attempts to kill Cersei.*** "
            "Your response should directly convert the user's action into a character's attempt without adding any explanations or modifications to the original action. "
            "Simply translate the user's intent into the character’s attempted action, maintaining the original intention as closely as possible. "
            "Output the character's name followed by their (attempted) action in a concise manner."
        )

        parsed_input = self.chat.send_message(prompt, keep_in_history=False) + '\n\n\n'
        if self.debug:
            print(f"parsing the input from the user: {user_input}\n result: {parsed_input}\n")
        return parsed_input

    def achievement_evaluator(self):
        prompt = (f"SYSTEM: Here are the achievements available:***\n{self.achievements}***"
                  f"change the achievement's accomplished status to true if the user has achieved it."
                  f"Unless there is direct evidence in our message history"
                  f"do not change the status of the achievements from False to True."
                  f"Output the updated achievements(match the format provided to you) in json format:")
        resp = self.chat.send_message(prompt, keep_in_history=False)
        resp = resp.replace("json", "").replace("```", "")
        try:
            achievements = json.loads(resp)
            if "achievements" in achievements:
                resp = json.dumps(achievements["achievements"])
        except Exception:
            pass
        self.achievements = resp
        if self.debug:
            print(f"achievement_evaluator\nresp: {resp}\n\n")
        # return resp

    def get_achievements(self):
        return self.achievements

    def generate_result(self, user_input: str):
        """
        takes in new event, asks for the user
        :param user_input:
        :return:
        """
        choice = self.action_evaluator(user_input)
        prompt = (f"SYSTEM: Consider the outcome of the event: ***{self.chosen_event_plot}*** regarding\n"
                  f"Astarion's action: ***{choice}***\n"
                  f"Consider these questions when developing the outcome:\n"
                  f"1. Is the decision logically possible in the context of ASOIAF?(e.g. the user can't introduce someone who does not exist in ASOIAF world)\n"
                  f"2. Is Astarion capable of making such actions?(e.g. Astarion does not know Joffery's bastardy unless mentioned in previous conversation)\n"
                  f"3. realism is key, Astarion cannot do impossible things for humans(e.g. Astarion cannot fly or teleport or change into a monster)\n"
                  f"4. The outcome should be a direct result of Astarion's decision.\n"
                  f"5. If you deem the action logically impossible, be creative and present a humorous result(how he attempted to but failed)\n"
                  f"6. Do not change the Astarion's action.\n"
                  f"7. Give a clear, definite result of the event\n"
                  f"The result of  50 word paragraph:")
        prompt = (f"SYSTEM: Evaluate the event's outcome: ***{self.chosen_event_plot}*** in light of\n"
                  f"Astarion's chosen action: ***{choice}***.\n"
                  f"When crafting the outcome, consider the following critical aspects:\n"
                  f"1. Logical Consistency: Ensure the action fits within the ASOIAF universe. (For instance, introducing non-existent characters is off-limits.)\n"
                  f"2. Character Capability: Assess if Astarion has the knowledge and skills to execute the action. (e.g., Astarion is unaware of Joffrey's illegitimacy unless previously discussed.)\n"
                  f"3. Realism: Astarion's actions must be within human capabilities; supernatural feats like flying or teleporting are not permitted.\n"
                  f"4. Direct Consequence: The outcome must be a direct consequence of Astarion's action.\n"
                  f"5. Creativity in Constraints: If the action is deemed logically impossible, craft a humorous narrative on how Astarion's attempt unfolds and fails.\n"
                  f"6. Action Integrity: Do not alter Astarion's original action.\n"
                  f"7. Give a clear, definite result of the event\n"
                  f"Craft a concise outcome in a paragraph of approximately 50 words:")
        result = self.chat.send_message(prompt, keep_in_history=False) + '\n\n'
        self.summarize_player_action(choice, result)
        self.achievement_evaluator()
        if self.debug:
            print(f"generated result:\n {result}\n")
        return choice + '\n' + result

    def summarize_player_action(self, choice: str, result: str):
        prompt = (f"SYSTEM: Event : *{self.chosen_event_plot}*\nser Astarion's action: *{choice}*\n final result: *{result}\n"
                  f"Summarize the whole event above into a single, concise paragraph less than 30 words only including"
                  f" the event, astarion's action, and the result.")
        resp = self.chat.send_message(prompt, keep_in_history=False) + '\n\n'
        self.chat.add_to_message_history(resp, False)
        self.chat.add_to_message_history("I will remember this change to plot", True)

    def pick_event_id(self, beg: int, end: int):
        return beg
        # chosen_id = random.randint((beg + end + 1) // 2, end)
        # prompt = (f"SYSTEM: Choose the most important event in the plot "
        #           f"from this list:***\n{generate_context(beg, end, include_id=True)}***\n"
        #           f"Only output one numeric number representing the event's ID\n"
        #           f"Your number:")
        # resp = self.chat.generate_content(prompt)
        # if self.debug:
        #     print("pick_event_id\n", resp, '\n\n')
        # if resp[0:2] == 'id':
        #     resp = resp[2:]
        # return int(resp)

    def part_by_part_summery(self, beg: int, end: int, gap=GAP):
        """
        Add summery to history
        """
        if beg > end:
            return ""
        full_summery = ""
        while beg <= end:
            if beg + gap >= end:
                event_summery = self.generate_background_summery(beg, end)
            else:
                event_summery = self.generate_background_summery(beg, beg + gap)
            # self.chat.add_to_message_history("our version of plot:" + event_summery + '\n', False)
            # self.chat.add_to_message_history("I will remember this plot"'\n', True)
            full_summery += event_summery
            # if self.debug:
            #     print("new version of plot summery: ", event_summery, '\n\n')
            beg += gap + 1
            if beg > end:
                break
        return full_summery

    def initial_loop(self):
        end = self.current_event_id + GAP - 1
        if end >= TOTAL_EVENTS:
            end = TOTAL_EVENTS - 1

        chosen_event_id = self.pick_event_id(self.current_event_id, end)
        full_summery = self.part_by_part_summery(self.current_event_id, chosen_event_id - 1)
        self.chosen_event_plot = self.generate_new_event(chosen_event_id)
        self.current_event_id = chosen_event_id + 1
        return full_summery + self.chosen_event_plot

    def next_loop(self, user_input):
        end = self.current_event_id + GAP
        if end >= TOTAL_EVENTS:
            end = TOTAL_EVENTS - 1
        result_of_event = self.generate_result(user_input)
        if self.debug:
            print("CHAT HISTORY: ", self.chat.chat_history)
        if self.current_event_id >= TOTAL_EVENTS:
            return result_of_event
        chosen_event_id = self.pick_event_id(self.current_event_id, end)
        full_summery = self.part_by_part_summery(self.current_event_id, chosen_event_id - 1)
        self.chosen_event_plot = self.generate_new_event(chosen_event_id)
        self.current_event_id = chosen_event_id + 1
        return result_of_event + full_summery + self.chosen_event_plot

    def get_conversation_history(self) -> list[str]:
        if self.debug:
            print("request chat history: ", [i.content for i in self.chat.chat_history.messages if i.content != "I will remember this change to plot"])
        return [i.content for i in self.chat.chat_history.messages if i.content != "I will remember this change to plot"]


if __name__ == "__main__":
    game = Game(True)
    print(game.initial_loop())
    while True:
        message = input()
        print(game.next_loop(message))
