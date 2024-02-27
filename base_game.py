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
        prompt = (f"In the original timeline:*** {generate_context(beg, end)}*** "
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
        # if self.debug:
        #     print(f"generating new event for id{end}, which is {events[end]}\n\n")
        prompt = (f"Adapting the event: \"{events[end]}\" to ser Astarion's past action, if any. "
                  f"Consider these questions when formulating your plot:"
                  f"1. What did astarion do in the past? unless mentioned, he does NOT alter the plot.\n"
                  f"2. Are the people in these events directly affected by past actions of astarion?\n"
                  f"3. If they are directly influenced by astarion, how might their role in the events change?\n"
                  f"Detail how this event unfolds, emphasizing ***ser Astarion***'s role."
                  f"Do not present the outcome of this event!"
                  f"Present 2 possible choices for ***ser Astarion*** in this event. "
                  f"Present a third choice prompting the user to make a custom decision"
                  f"Your 50 word paragraph elaborating on the event's unfold:")
        # self
        return self.chat.send_message(prompt, keep_in_history=False) + '\n\n\n'

    def action_evaluator(self, user_input: str):
        """
        Evaluates the User's action
        :param user_input:
        :return:
        """
        prompt = (f"Here is the current event: ***{self.chosen_event_plot}***"
                  f"The user made a decision of ***{user_input}***"
                  f"You should check for deterministic statements and change them into attempts."
                  f"e.g. user says ***I want to kill Cersi*** parse it into *** Astarion attempts to kill Cersi."
                  f"e.g. user says ***I fly to Kings Landing*** parse it into ***Astarion jumps into the sky and tries to fly***."
                  f"parse user input into an attempt by Astarion's"
                  f"breifly output Astarion's action in 20 words:")
        parsed_input = self.chat.send_message(prompt, keep_in_history=False) + '\n\n\n'
        if self.debug:
            print(f"parsing the input from the user{user_input}\n result: {parsed_input}\n")
        return parsed_input

    def achievement_evaluator(self):
        prompt = (f"Here are the achievements available:***\n{self.achievements}***"
                  f"change the achievement's accomplished status to true if the user has achieved it."
                  f"Unless there is clear evidence in our message history, do not change the status of the achievements from False to True."
                  f"Output in json format the updated achievements:")
        resp = self.chat.send_message(prompt, keep_in_history=False)
        resp = resp.replace("json", "").replace("```", "").replace("\n", "")
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
        prompt = (f"Considering ***ser Astarion***'s decision: \"{choice}\", "
                  f"how does it influence the outcome of the event: {self.chosen_event_plot}? "
                  f"Consider these questions when developing the outcome:"
                  f"1. Is the decision possible in the context of ASOIAF?\n"
                  f"2. Is Astarion capable of making such decisions?(e.g. Astarion does not know Joffery's birth unless mentioned in previous conversation)\n"
                  f"3. realism is key, Astarion cannot do impossible things (e.g. Astarion cannot fly or teleport or win in a fight against the mountain)\n"
                  f"4. The outcome should be a direct result of Astarion's decision, "
                  f"Your paragraph:")

        result = self.chat.send_message(prompt, keep_in_history=False) + '\n\n'
        self.summarize_player_action(choice, result)
        self.achievement_evaluator()
        if self.debug:
            print(f"generated result:\n {result}\n")
        return result

    def summarize_player_action(self, choice: str, result: str):
        prompt = (f"Event: *{self.chosen_event_plot}*\nser Astarion's action: *{choice}*\n final result: *{result}\n"
                  f"Summarize the whole event above into a single, concise paragraph of 50 words")
        resp = self.chat.send_message(prompt, keep_in_history=False) + '\n\n'
        self.chat.add_to_message_history(resp, False)
        self.chat.add_to_message_history("I will remember this", True)

    def pick_event_id(self, beg: int, end: int):
        # chosen_id = random.randint((beg + end + 1) // 2, end)
        # return chosen_id
        prompt = (f"Choose the most important event in the plot "
                  f"from this list:***\n{generate_context(beg, end, include_id=True)}***\n"
                  f"Only output one numeric number representing the event's ID\n"
                  f"Your number:")
        resp = self.chat.generate_content(prompt)
        if self.debug:
            print("pick_event_id\n", resp, '\n\n')
        if resp[0:2] == 'id':
            resp = resp[2:]
        return int(resp)

    def part_by_part_summery(self, beg: int, end: int, gap=GAP):
        """
        Add summery to history
        """
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
        end = self.current_event_id + GAP
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

        chosen_event_id = self.pick_event_id(self.current_event_id, end)
        full_summery = self.part_by_part_summery(self.current_event_id, chosen_event_id - 1)
        self.chosen_event_plot = self.generate_new_event(chosen_event_id)
        self.current_event_id = chosen_event_id + 1
        return result_of_event + full_summery + self.chosen_event_plot


if __name__ == "__main__":
    game = Game(True)
    print(game.initial_loop())
    while True:
        message = input()
        print(game.next_loop(message))
