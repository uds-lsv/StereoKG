"""
Refer:
https://github.com/Aunsiels/CSK/tree/master/quasimodo
"""

import os
import question_to_statement as q2s
import inflect
inflect=inflect.engine()

CACHE_DIR = "./question2statement/"

class StatementMaker(object):

    def __init__(self, use_cache=True):
        self._filename = "./stmt_cache.tsv"
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        self._use_cache = use_cache
        # Load previous q2s
        self._q2s = dict()
        self._load_q2s()

    def _load_q2s(self):
        if not self._use_cache:
            return
        if os.path.isfile(CACHE_DIR + self._filename):
            with open(CACHE_DIR + self._filename, encoding="utf-8") as f:
                for line in f:
                    line = line.strip().split("\t")
                    if len(line) < 2:
                        continue
                    self._q2s[line[0]] = line[1]

    def _save_q2s(self, question, statement, subject):
        if not self._use_cache:
            return
        self._q2s[question] = statement
        with open(CACHE_DIR + self._filename, "a") as f:
            f.write(question.strip() + "\t" + statement.strip() +
                    "\t" + subject + "\n")

    def _process_makes(self, question, subject):
        idx=question.lower().index("what makes")
        ind=idx+len("what makes")+1
        if not inflect.singular_noun(subject):
            statement=question[ind:ind+len(subject)] + " is" + question[ind+len(subject):-1]
        else:
            statement=question[ind:ind+len(subject)] + " are" + question[ind+len(subject):-1]
        return statement

    def _process_dont(self, question, subject, is_dont):
        if subject in question:
            idx = question.lower().index(subject)
            if is_dont:
                question = question[:idx+len(subject)] + " don't " + question[idx+len(subject):]
        
        if question.startswith("nt"):
            question = question[3:]
        elif " nt " in question:
            question = question.replace(" nt", "")

        return question

    def to_statement(self, question, subject, safe_source=False):
        question = question.replace("&amp;", " & ").replace("&gt;", " > ").replace("&lt;", " < ")
        is_dont = False
        if question.strip() in self._q2s:
            return self._q2s[question.strip()]
        question = question.replace(" cant ", " can't ")
        pos, tokens = q2s.get_pos_and_tokens_from_question(question)
        if len(pos) <= 2:
            return ""
        # Correct nano - particule
        tokens, pos = q2s._correct_tokens(tokens, pos)

        # replace n't by not
        to_negate = None
        negated_verb = None
        for i, token in enumerate(tokens):
            if token == "n't" and i-1 >= 0 and tokens[i-1] in q2s.NEGATE_VERB:
                to_negate = i-1
                break
        if to_negate is not None:
            del tokens[to_negate + 1]
            del pos[to_negate + 1]
            negated_verb = tokens[to_negate]

        if q2s.is_form_of_be(tokens[1]) and len(tokens) == 4:
            statement = " ".join([tokens[2], tokens[1], tokens[3]])
        elif q2s.is_form_of_be(tokens[1]) and q2s.is_personal_pronoun(tokens[2]):
            statement = " ".join([tokens[2], tokens[1]] + tokens[3:])
        elif q2s.is_form_of_be(tokens[1]):
            statement = q2s.process_general_be_form(pos, tokens, subject)
        elif q2s.is_form_do_present(tokens[1]):
            statement = " ".join(tokens[2:])
        elif q2s.is_form_of_can(tokens[1]):
            statement = q2s.process_can_form(pos, tokens)
        elif tokens[1] == "ca" and tokens[2] == "n't":
            statement = self.process_ca_nt(subject, tokens)
        elif not q2s.is_modal_or_auxiliary(tokens[1]):
            statement = " ".join(tokens[1:])
        else:
            statement=question
        
        if "don't" in question.lower():
            question = question.replace(" don't ", " do not ")
            is_dont = True
        
        elif "dont" in question.lower():
            question = question.replace(" dont ", " do not ")
            is_dont = True
            
        if "what makes" in question.lower():
            statement = self._process_makes(question, subject)

        if negated_verb is not None:
            statement_split = statement.split(" ")
            position_verb = None
            for i, word in enumerate(statement_split):
                if word == negated_verb:
                    position_verb = i
                    break
            if position_verb is not None:
                statement_split.insert(i+1, "not")
                statement = " ".join(statement_split)
        
        statement = self._process_dont(statement, subject, is_dont)

        if not safe_source:
            statement = q2s.correct_statement(statement)
        self._save_q2s(question, statement, subject)
        return statement

    def process_ca_nt(self, subject, tokens):
        # I have to turn it to an affirmation to make openIE work
        temp = self.to_statement(tokens[0] + " can " +
                                 " ".join(tokens[3:]), subject)
        statement = temp
        return statement