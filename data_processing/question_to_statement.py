import spacy
import logging
import time
from subprocess import call
from inflection import InflectAccessor
import language_tool_python as ltpy

DEFAULT_INFLECT = InflectAccessor()
_tool = ltpy.LanguageTool('en-US')
#_tool = ltpy.LanguageToolPublicAPI('en-US')
_nlp = spacy.load('en_core_web_sm')

TEXT = 0
POS = 1


NEGATE_VERB = ["am", "is", "are", "was", "were", "do", "does", "did",
               "should", "must", "would", "may", "have", "has",
               "might", "shall", "will", "could"]


def _correct_tokens(tokens, pos):
    merge_next = False
    res_tokens = []
    res_pos = []
    for i in range(len(tokens)):
        if tokens[i] == "-" and res_tokens:
            res_tokens[-1] = res_tokens[-1] + "-"
            res_pos[-1] = (res_pos[-1][0] + "-", res_pos[-1][1])
            merge_next = True
        elif merge_next:
            merge_next = False
            res_tokens[-1] = res_tokens[-1] + tokens[i]
            res_pos[-1] = (res_pos[-1][0] + pos[i][0], pos[i][1])
        else:
            res_tokens.append(tokens[i])
            res_pos.append(pos[i])
    return res_tokens, res_pos


def is_form_of_be(word):
    return word in ["are", "is", "was", "were", "am", "be"]


def is_personal_pronoun(word):
    return word in ["their", "it", "i", "they", "she", "he", "we", "you","there"]


def is_form_of_can(word):
    return word in ["can", "could", "cannot", "can't"]


def is_form_do_present(word):
    return word in ["do", "does"]


def is_modal_or_auxiliary(word):
    return is_form_of_can(word) or is_form_of_be(word) or is_form_do_present(word) or \
    word in ["should", "must", "would", "may", "did", "have", "has", "might", "shall", "will"] or \
    "n't" in word


def get_pos_and_tokens_from_question(question):
    tokens = []
    pos = []
    for token in _nlp(question):
        if token.text == "'s":
            tokens[-1] = tokens[-1] + "'s"
            pos[-1] = (pos[-1][TEXT] + "'s", pos[-1][POS])
        elif token.text == "?":
            continue
        else:
            tokens.append(token.text)
            pos.append((token.text, token.tag_))
    return pos, tokens


def clean_multiple_parts(begin, middle, end, tokens):
    if middle and middle[0] == tokens[1]:
        middle = middle[1:]
    if end and end[0] == tokens[1]:
        end = end[1:]
    if begin[-1] == "not":
        begin = begin[:-1]
        middle = ["not"] + middle
    return begin, middle, end


def build_statement_from_multiple_parts(begin, middle, end, found_in, tokens, tokens_begin):
    begin = [x for x in begin if x != tokens[1]]
    if len(begin) == 0:
        statement = ""
    elif len(middle) == 0 and len(end) == 0:
        statement = ""
    elif len(middle) == 0:
        statement = " ".join(begin) + " " + tokens[1] + \
                    " " + " ".join(end)
    elif len(end) == 0:
        statement = " ".join(begin) + " " + tokens[1] + " " + \
                    " ".join(middle)
    elif found_in:
        statement = " ".join(begin) + " " + tokens[1] + " " + \
                    " ".join(middle) + \
                    " " + \
                    " ".join(end)
    elif tokens[1] == "are" and "NN" in tokens_begin[-1] \
            and tokens[0] == "why":
        statement = " ".join(begin) + " have " + " ".join(middle) + \
                    " " + \
                    " ".join(end)
    else:
        mid = " ".join(middle)
        if mid.startswith(tokens[1] + " "):
            statement = " ".join(begin) + " " + " ".join(end) + " " + \
                        mid
        else:
            statement = " ".join(begin) + " " + " ".join(end) + " " + \
                        tokens[1] + " " + mid
    return statement


def process_general_be_form(pos, tokens, subject):
    subject_plural = DEFAULT_INFLECT.to_plural(subject)
    begin = []
    middle = []
    end = []
    tokens_begin = []
    found_noun = False
    found_second = False
    found_something_else = False
    found_final_adj = False
    found_cc = False
    found_in = False
    for i in range(2, len(pos)):
        current_text_pos = pos[i]
        subject_appeared = (subject in " ".join(begin) + " " + current_text_pos[TEXT] or
                            subject_plural in " ".join(begin) + " " + current_text_pos[TEXT])
        if not found_noun and subject_appeared and (
                not found_cc or "NN" in current_text_pos[POS] or "VBZ" in current_text_pos[POS]):
            if (tokens[1] != "are" or "NNS" == current_text_pos[1] or found_cc or "CC" in current_text_pos[POS]
                or (i != len(pos) - 1 and "NN" in current_text_pos[POS] and (
                            "RB" in pos[i + 1][POS] or "JJ" in pos[i + 1][POS]))) \
                    and (current_text_pos[POS] != "VBG" and current_text_pos[POS] != "DT" and
                         ("JJ" not in current_text_pos[POS] or len(pos) < 8)):
                if "CC" in current_text_pos[POS]:
                    found_cc = True
                elif found_cc and "NN" in current_text_pos[POS]:
                    found_noun = True
                elif not found_cc:
                    found_noun = True
            begin.append(current_text_pos[TEXT])
            tokens_begin.append(current_text_pos[POS])
        elif found_noun and not found_something_else and \
                not found_second and ("CC" in current_text_pos[POS] or "of" == current_text_pos[TEXT]):
            found_cc = True
            found_noun = False
            begin.append(current_text_pos[TEXT])
            tokens_begin.append(current_text_pos[POS])
        elif found_noun and not found_something_else and found_second \
                and ("CC" in current_text_pos[POS] or "of" == current_text_pos[TEXT]):
            found_second = False
            end.append(current_text_pos[TEXT])
        elif not found_something_else and found_noun and \
                ("NN" in current_text_pos[POS] or "IN" in current_text_pos[0]) \
                and not found_final_adj:
            if "IN" in current_text_pos[TEXT]:
                found_in = True
            found_second = True
            end.append(current_text_pos[TEXT])
        elif not found_noun:
            begin.append(current_text_pos[TEXT])
        else:
            if "JJ" in current_text_pos[POS]:
                found_final_adj = True
            found_something_else = True
            middle.append(current_text_pos[TEXT])
    begin, middle, end = clean_multiple_parts(begin, middle, end, tokens)
    statement = build_statement_from_multiple_parts(begin, middle, end, found_in, tokens, tokens_begin)
    return statement


def process_can_form(pos, tokens):
    statement = ""
    if len(tokens) == 4:
        statement = tokens[2] + " " + tokens[1] + " " + tokens[3]
    else:
        # Look for first verb, in base form
        found_noun = False
        for i in range(len(pos)):
            current_text_pos = pos[i]
            if current_text_pos[1] == "VBP" or current_text_pos[1] == "VB" and found_noun:
                statement = " ".join(tokens[2:i]) + " " + tokens[1] + " " + " ".join(tokens[i:])
                break
            elif "NN" in current_text_pos[1]:
                found_noun = True
    return statement


def correct_statement(statement):
    if len(statement.strip()) == 0:
        return ""
    global _tool
    try:
        matches = _tool.check(statement)
        is_bad_rule = lambda rule: rule.message == 'Possible spelling mistake found.' and len(rule.replacements) and rule.replacements[0][0].isupper()
        matches = [rule for rule in matches if not is_bad_rule(rule)]
    except:
        try:
            logging.error("Problem with LanguageTools for " + statement)
            time.sleep(60)
            try:
                del _tool
            except NameError:
                pass
            time.sleep(10)
            call(["killall", "java"])
            time.sleep(10)
            try:
                _tool = ltpy.LanguageTool('en-US')
            except:
                raise
            return correct_statement(statement)
        except:
            logging.error("Problem with LanguageTools for " + statement)
            raise
    return ltpy.utils.correct(statement, matches)