from colorama import Fore, Back, Style

class Sentence:

    def __init__(self, t: str, lab=[]):
        self.text = t
        self.labels = lab

    def get_labels(self):
        return self.labels

    def get_text(self):
        return self.text

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

    def get_encompassed_labels(self, alllabels, type: str, encompassing):
        relevant_labels = []
        for label in encompassing:
            relevant_labels = relevant_labels + self.get_labels_inbetween(alllabels, type, label['begin'], label['end'])
        return relevant_labels

    def get_labels_inbetween(self, alllabels, type, begin: int, end: int):
        relevant_labels = []
        for label in alllabels:
            if label['begin'] >= begin and label['end'] <= end and label['label'] == type:
                relevant_labels.append(label)
        return relevant_labels

    def get_labels_of_level(self, toplevel: bool):
        if toplevel:
            return list(filter(lambda l: (l['label'].startswith('Cause')) or (l['label'].startswith('Effect') or (l['label'] in ['Conjunction', 'Disjunction'])), self.labels))
        else: 
            return list(filter(lambda l: (l['label'] in ['Variable', 'Condition', 'Negation']), self.labels))

    def __str__(self):
        if len(self.labels) == 0:
            return self.text
        else: 
            colored = self.text

            color_annotations = []
            bgc = None
            bgcdefault = Back.BLACK
            for label in self.get_labels_of_level(True):
                if label['label'].startswith('Cause'):
                    bgc = Back.RED
                elif label['label'].startswith('Effect'):
                    bgc = Back.BLUE
                elif label['label'] == 'Conjunction':
                    bgc = Back.LIGHTBLUE_EX
                elif label['label'] == 'Disjunction':
                    bgc = Back.LIGHTGREEN_EX

                color_annotations.append({
                    'index': label['begin'],
                    'color': bgc + Style.BRIGHT}
                    )
                color_annotations.append({
                    'index': label['end'],
                    'color': bgcdefault + Style.RESET_ALL}
                    )

            fgc = None
            fgcdefault = Fore.WHITE
            for label in self.get_labels_of_level(False):
                if label['label'] == 'Variable':
                    fgc = Fore.LIGHTBLUE_EX
                elif label['label'] == 'Condition':
                    fgc = Fore.LIGHTGREEN_EX
                elif label['label'] == 'Negation':
                    fgc = Fore.RED

                color_annotations.append({
                    'index': label['begin'],
                    'color': fgc + Style.BRIGHT}
                    )
                color_annotations.append({
                    'index': label['end'],
                    'color': fgcdefault + Style.NORMAL}
                    )

            # order the color annotations
            color_annotations.sort(key=lambda a: a['index'], reverse=False)
            
            offset = 0
            for annotation in color_annotations:
                colored = colored[:annotation['index']+offset:] + annotation['color'] + colored[annotation['index']+offset:]
                offset += len(annotation['color'])

            colored = colored + Fore.RESET + Back.RESET
            return colored
