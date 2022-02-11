from colorama import Fore, Back, Style

class Sentence:

    def __init__(self, sen: str, lab=[]):
        self.sentence = sen
        self.labels = lab

    def get_labels(self):
        return self.labels

    def get_causal_labels(self):
        # obtain all labels that begin with 'Cause' or 'Effect'
        all_causal_labels = self.get_labels_of_type(self.labels, 'Cause') + self.get_labels_of_type(self.labels, 'Effect')

        # group all labels that represent the same event but are distinct (e.g., because an event is split within a sentence)
        causal_labels = {}
        for event in all_causal_labels:
            if event['label'] not in causal_labels.keys():
                causal_labels[event['label']] = []
            causal_labels[event['label']].append(event)
        return causal_labels

    def get_labels_of_type(self, labels, type: str):
        relevant_labels = []
        for label in labels:
            if label['label'].startswith(type):
                relevant_labels.append(label)
        return relevant_labels

    def get_causal_labels(self):
        causal = list(filter(lambda l: (l['label'].startswith('Cause')) or (l['label'].startswith('Effect')), self.labels))
        return causal

    def __str__(self):
        if len(self.labels) == 0:
            return self.sentence
        else: 
            colored = self.sentence

            io = 0
            bgc = None
            for label in self.get_causal_labels():
                if label['label'].startswith('Cause'):
                    bgc = Back.MAGENTA
                elif label['label'].startswith('Effect'):
                    bgc = Back.CYAN

                colored = colored[:label['begin']+io] + bgc + Fore.BLACK + colored[label['begin']+io:label['end']+io] + Back.RESET + Fore.RESET + colored[label['end']+io:]
                io = io + 20

            colored = colored + Fore.RESET + Back.RESET
            return colored
