from pathlib import Path
from chat import Chat
import random

DATA_PATH = "improved_data_v2.txt"
with open(DATA_PATH, 'r', encoding="utf-8") as file:
    events = file.readlines()
TOTAL_EVENTS = len(events)
GAP = 10


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

    def generate_background_summery(self, beg, end):
        prompt = (f"""# Role: BackgroundNarratorGPT

## Profile
- Author: Game Developer
- Version: 0.1
- Language: English
- Description: Generate a background summary from a series of events, making adjustments only when there is clear evidence of Ser Astarion's involvement. The focus is on seamlessly integrating Ser Astarion's actions into the existing plot, provided his participation is explicitly mentioned or strongly implied.

## Skills
- Synthesize event details into a cohesive background story, adjusting only for confirmed involvement of Ser Astarion.
- Exclude time information for a timeless narrative.
- Critically assess and identify Ser Astarion's documented or implied influence on the events and characters.

## Rules
1. Do not include time information in summaries.
2. Make changes to the plot only if there is clear evidence or strong implication of Ser Astarion's involvement in the events.
3. Maintain concise and coherent narrative construction, ensuring Ser Astarion's role is highlighted only where it directly affects the storyline.

## Workflow
1. Analyze the input events for explicit mentions or strong implications of Ser Astarion's involvement.
2. Determine the nature and extent of Ser Astarion's past actions' influence on the plot, making alterations only when his participation is clearly indicated.
3. Craft a summary that integrates Ser Astarion's actions with the original plot, adjusting the narrative solely based on confirmed evidence of his involvement.

## Task
Generate the background summary based on the provided events, adjusting the narrative to include Ser Astarion's role only where his involvement is clearly indicated or strongly implied.

Events:
{generate_context(beg, end)}""")

        beck_ground_summery = self.chat.send_message(prompt, keep_in_history=False) + '\n\n'
        if self.debug:
            print(f"generating background_summery for id{beg, end}\nsummery:{beck_ground_summery}\n\n")
        return beck_ground_summery

    def generate_new_event(self, end):
        if self.debug:
            print(f"generating new event for id{end}, which is {events[end]}\n\n")
        prompt = (f"""
# Role: EventCreatorGPT

## Profile
- Author: Game Developer
- Version: 0.1
- Language: English
- Description: Adapt an existing event to include Ser Astarion's involvement, focusing on how his actions could unfold without concluding the event's outcome.

## Skills
- Creative adaptation of events to include character influence.
- Suggesting possible actions for Ser Astarion within the event.

## Rules
1. Detail Ser Astarion's role without finalizing the event's outcome.
2. Present possible choices for Ser Astarion.

## Workflow
1. Receive the event details.
2. Adapt the event to highlight Ser Astarion's involvement.

## Task
Adapt the given event to include Ser Astarion's role, detailing his possible actions without resolving the event.\n
{events[end]}""")
        # self
        return self.chat.send_message(prompt, keep_in_history=False) + '\n\n\n'

    def generate_result(self, user_input: str):
        """
        takes in new event, asks for the user
        :param user_input:
        :return:
        """
        choice = user_input
        prompt = (f"""
## Profile
- Author: Game Developer
- Version: 0.1
- Language: English
- Description: Based on Ser Astarion's chosen action, determine the outcome of the event, focusing on immediate consequences and integrating them into a coherent summary.

## Skills
- Analyzing player choices to determine logical outcomes.
- Summarizing the consequences of Ser Astarion's actions.

## Rules
1. Base the event's outcome on Ser Astarion's decision.
2. Focus on immediate impacts without extrapolating too far into the plot.

## Workflow
1. Consider Ser Astarion's decision.
2. Analyze its influence on the event.
3. Summarize the event's outcome, emphasizing the consequences of the chosen action.

## Task
Based on Ser Astarion's chosen action, determine and summarize the outcome of the event.
Event: *{self.chosen_event_plot}*
***ser Astarion***'s decision: \"{choice}\"
""")

        result = self.chat.send_message(prompt, keep_in_history=False) + '\n\n'
        self.summarize_player_action(choice, result)
        if self.debug:
            print(f"The changed result for this event is {result}")
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

    def part_by_part_summery(self, beg: int, end: int, gap=GAP // 3):
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
            if self.debug:
                print("new version of plot summery: ", event_summery, '\n\n')
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
