from pathlib import Path
from chat import Chat

DATA_PATH = "improved_data_v2.txt"
with open(DATA_PATH, 'r', encoding="utf-8") as file:
    events = file.readlines()
TOTAL_EVENTS = len(events)
GAP = 20
SUMMERY_EXAMPLE = "Eddard Stark becomes Hand of the King and has a secret meeting with Catelyn to discuss Bran's attempted murder and the Lannisters. Jon Snow learns of Bran's survival and improves his fighting skills at the Night's Watch, where Tyrion Lannister offers him support before leaving. Arya and Sansa Stark's conflict leads to Eddard emphasizing family bonds. Arya begins swordsmanship lessons with Syrio Forel. Eddard receives news of Bran's recovery and investigates Jon Arryn's death, getting crucial information from Petyr Baelish. Samwell Tarly joins the Night's Watch, establishing a significant friendship with Jon."


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

    def generate_background_summery(self, beg, end):
        prompt = (f"Referencing the the original plot:{generate_context(beg, end)}. "
                  f"and combining the current changes to the plot of A Song of Ice and Fire "
                  f"what will be the new plot that replaces the original plot? "
                  f"Your don't have to include all of the events, "
                  f"but you need to keep the new plot organized inside your paragraph. "
                  f"And you new plot will only cover the same topics as the original plot"
                  f"Your paragraph in 100 words:")
        beck_ground_summery = self.chat.send_message(prompt, keep_in_history=True)
        if self.debug:
            print(f"generating background_summery for id{beg, end}\nsummery:{beck_ground_summery}\n\n")
        return beck_ground_summery

    def generate_new_event(self, end):
        if self.debug:
            print(f"generating new event for id{end}, which is {events[end]}\n\n")
        prompt = (f"Further Developing on our plot,"
                  f"Adapt this event {events[end]} "
                  f"to logically fit our revised plot "
                  f"elaborate on how the new version of this event will unfold "
                  f"and tell me ***ser Astarion***'s role in the story"
                  f"Do not tell the end of the story as that will depend on his actions "
                  "You will present a choice for ***ser Astarion***"
                  f"Your paragraph in 100 words:")
        return self.chat.send_message(prompt, keep_in_history=True) + '\n\n'

    def generate_result(self, user_input: str):
        """
        takes in new event, asks for the user
        :param new_event:
        :return:
        """
        choice = user_input
        prompt = (f"Based on our version of the plot, and the current "
                  f"event: ***{self.chosen_event_plot}*** "
                  f"what is the result of the current event based on ***ser Astarion***'s "
                  f"action{choice}? "
                  f"Only provide the result for this specific event"
                  f"Do not explain the changes made, just output one paragraph of our version of the plot"
                  f"Your paragraph:")
        result = self.chat.send_message(prompt, keep_in_history=True)
        if self.debug:
            print(f"The changed result for this event is {result}")
        return result

    # def get_user_input(self):
    #     return input()
    #     if self.debug:
    #         return input()
    #     else:
    #         raise NotImplementedError

    def pick_event_id(self, beg: int, end: int):
        prompt = (f"Choose the most important event for the plot of A Song of I and Fire "
                  f"from this list:{generate_context(beg, end, include_id=True)}"
                  f" The most important event is id(only output one number):")
        resp = self.chat.generate_content(prompt)
        if resp[0:2] == 'id':
            resp = resp[2:]
        return int(resp)

    def part_by_part_summery(self, beg: int, end: int, gap=5):
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
            full_summery += event_summery + '\n\n'
            if self.debug:
                print("new version of plot summery: ", event_summery, '\n\n')
            beg += gap
            if beg >= end:
                break
        return full_summery

    # def main_loop(self):
    #
    #     while self.current_event_id < TOTAL_EVENTS:

    def initial_loop(self):
        end = self.current_event_id + GAP
        if end >= TOTAL_EVENTS:
            end = TOTAL_EVENTS - 1

        chosen_event = self.pick_event_id(self.current_event_id, end)
        full_summery = self.part_by_part_summery(self.current_event_id, chosen_event - 1)
        self.chosen_event_plot = self.generate_new_event(chosen_event)
        self.current_event_id = end + 1
        return full_summery + self.chosen_event_plot
        # print("Current event:\n", chosen_event_plot, '\n\n')
        # print(f"Event: {chosen_event_plot}\n Enter your choice:")  # change to API input
        # result_of_event = self.generate_result(chosen_event_plot)
        # print("Result:\n", result_of_event, '\n\n')

    def next_loop(self, user_input):
        end = self.current_event_id + GAP
        if end >= TOTAL_EVENTS:
            end = TOTAL_EVENTS - 1

        result_of_event = "Result of event:\n" + self.generate_result(user_input)
        print("Result:\n", result_of_event, '\n\n')

        chosen_event = self.pick_event_id(self.current_event_id, end)
        full_summery = self.part_by_part_summery(self.current_event_id, chosen_event - 1)
        self.chosen_event_plot = self.generate_new_event(chosen_event)
        print("Current event:\n", self.chosen_event_plot, '\n\n')
        print(f"Event: {self.chosen_event_plot}\n Enter your choice:")  # change to API input
        # self.chat.add_to_message_history(chosen_event_plot, False)
        # self.chat.add_to_message_history(result_of_event, False)
        # OUTPUT result, now we use cli
        self.current_event_id = end + 1
        return result_of_event + full_summery + self.chosen_event_plot
        # if end == TOTAL_EVENTS - 1:
        #     break


if __name__ == "__main__":
    game = Game(False)
    print(game.initial_loop())
    while True:
        message = input()
        print(game.next_loop(message))
