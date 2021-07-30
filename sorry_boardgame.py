# Jeffrey Andersen
# This program was developed starting July 08, 2021, as the Sorry! boardgame in a console-app format.
# future consideration: collect stats on players
# future consideration: animate pawn movements on the board
# future consideration: allow multiple players to view the board at the same time via different screens (considering that in physical play players can ponder what to do on their turn by examining the board before their next turn arrives)
# future consideration: confirm deck composition is as it should be
# future consideration: change how the end of slides are labeled as the '0's can be hard to read through
# future consideration: as a player is playing a 7, give them the ability to undo how they have divvied up the movements (as opposed to cancelling the operation and starting from scratch)
# future consideration: better display for getting a number in a range from a user such that if there is only one numerical option, the user understands this and that inputting the sole number shown indicates using that number as the input value
# future consideration: if there is a default play on a turn, don't allow the player to try to pick a different valid play for the given card (unless the default play is not the only play)
# future consideration: some "invalid play" message when the user attempts an invalid play
# future consideration: playing until a number of points is achieved (5 points per opponent pawn not home, 25 points if opponents have at most two pawns home, 50 points if opponents have at most one pawn home, and 100 points if no opponent has any pawns home) where the winner goes first in subsequent rounds
# future consideration: use slide locations in Location enum to dynamically determine and mark the slide paths on the game board
# future consideration: scoring a play takes into consideration how other players are constrained by their cards in hand (for example, discarding is only allowed if a player had no valid plays (except possibly an '11' as a swap))
# future consideration: function annotations for the practice, improved readability, and reduced comment length
# future consideration: docstrings (https://www.python.org/dev/peps/pep-0257/) for the practice, improved readability, and reduced comment length
# future consideration: prompt user for confirmation of their play if their selected play has a score significantly lower than their possible play of highest score


import copy
import random
from enum import Enum
from os import system, name


class Color(Enum):  # maps color names to strings that, when printed, turn the subsequent text to that color
    # BLACK = '\033[0;30m'  # unused/unnecessary
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    # PURPLE = '\033[0;35m'  # unused/unnecessary
    # CYAN = '\033[0;36m'  # unused/unnecessary
    # WHITE = '\033[0;37m'  # unused/unnecessary
    RESET = '\033[0;0m'


class PlayerType(Enum):
    COMPUTER = 'c'
    HUMAN = 'h'
    NONEXISTENT = 'n'


class Coordinate(Enum):
    X = 'x'
    Y = 'y'
    MIN_X = 0
    MIN_Y = 0
    MAX_X = 15
    MAX_Y = 15


class Location(Enum):
    GREEN_START_EXIT = {Coordinate.X: 4, Coordinate.Y: 0}
    RED_START_EXIT = {Coordinate.X: 15, Coordinate.Y: 4}
    BLUE_START_EXIT = {Coordinate.X: 11, Coordinate.Y: 15}
    YELLOW_START_EXIT = {Coordinate.X: 0, Coordinate.Y: 11}
    HOME_COORDINATES = [{Coordinate.X: 2, Coordinate.Y: 6}, {Coordinate.X: 9, Coordinate.Y: 2}, {Coordinate.X: 13, Coordinate.Y: 9}, {Coordinate.X: 6, Coordinate.Y: 13}]
    GREEN_SAFETY_ZONE_ENTRANCE = {Coordinate.X: 2, Coordinate.Y: 0}
    RED_SAFETY_ZONE_ENTRANCE = {Coordinate.X: 15, Coordinate.Y: 2}
    BLUE_SAFETY_ZONE_ENTRANCE = {Coordinate.X: 13, Coordinate.Y: 15}
    YELLOW_SAFETY_ZONE_ENTRANCE = {Coordinate.X: 0, Coordinate.Y: 13}
    SLIDE_ENTRANCES = [{Coordinate.X: 1, Coordinate.Y: 0}, {Coordinate.X: 9, Coordinate.Y: 0}, {Coordinate.X: 15, Coordinate.Y: 1}, {Coordinate.X: 15, Coordinate.Y: 9}, {Coordinate.X: 14, Coordinate.Y: 15}, {Coordinate.X: 6, Coordinate.Y: 15}, {Coordinate.X: 0, Coordinate.Y: 14}, {Coordinate.X: 0, Coordinate.Y: 6}]
    # SLIDE_EXITS = [{Coordinate.X: 4, Coordinate.Y: 0}, {Coordinate.X: 13, Coordinate.Y: 0}, {Coordinate.X: 15, Coordinate.Y: 4}, {Coordinate.X: 15, Coordinate.Y: 13}, {Coordinate.X: 11, Coordinate.Y: 15}, {Coordinate.X: 2, Coordinate.Y: 15}, {Coordinate.X: 0, Coordinate.Y: 11}, {Coordinate.X: 0, Coordinate.Y: 2}]  # deprecated for not being utilized


class SpecialLocation(Enum):
    START = 's'
    HOME = 'h'


class CardSelectMethod(Enum):
    BY_INDEX = 'i'
    BY_VALUE = 'v'


def get_text_color(letter):
    if letter == Color.BLUE.name[0]:
        return Color.BLUE.value
    elif letter == Color.GREEN.name[0]:
        return Color.GREEN.value
    elif letter == Color.RED.name[0]:
        return Color.RED.value
    elif letter == Color.YELLOW.name[0]:
        return Color.YELLOW.value
    return Color.RESET.value


class Player:
    def __init__(self, player_color, player_type, max_hand_size):
        self.name = player_color.name.lower().capitalize()
        self.player_type = player_type  # PlayerType.COMPUTER for computer-controlled or PlayerType.HUMAN for human-controlled
        self.pawns = dict.fromkeys((self.name[0] + str(i) for i in range(1, 5)), SpecialLocation.START.value)  # pawn label and pawn x and y coordinates (zero indexed, on the game board (see where the game board is printed) cells (not individual characters), and where down and right are positive) or SpecialLocation.START.value for start or SpecialLocation.HOME.value for home of each of the player's four pawns
        self.cards_in_hand = []
        self.card_select_method = None if max_hand_size != 0 and self.player_type != PlayerType.COMPUTER else CardSelectMethod.BY_VALUE  # if there are no hands of cards or if this is a computer-controlled player, cards are selected by value
        if self.player_type == PlayerType.HUMAN:
            while self.card_select_method not in [CardSelectMethod.BY_INDEX.value, CardSelectMethod.BY_VALUE.value]:
                self.card_select_method = input(f"{get_text_color(self.name[0])}{self.name}{Color.RESET.value}, do you want to select cards to play from your hand by their 1-{max_hand_size} index ({CardSelectMethod.BY_INDEX.value}) or by their value ({CardSelectMethod.BY_VALUE.value})? ")
            if self.card_select_method == CardSelectMethod.BY_INDEX.value:
                self.card_select_method = CardSelectMethod.BY_INDEX
            elif self.card_select_method == CardSelectMethod.BY_VALUE.value:  # this last condition check is actually redundant
                self.card_select_method = CardSelectMethod.BY_VALUE


def clear_console():
    if name == 'nt':  # on a Windows machine
        system('cls')
    else:  # on a Mac or Linux machine where name == 'posix'
        system('clear')


def format_board_line(board_line, line_y_pos, all_pawns, is_which_pawns_placed):  # takes a board line string, the y value of the board line, list of all the pawns (which could be on the line) to be adjusted as pawns are placed, and list of whether each of those pawns has been placed, and returns both the board line with any pawns on it labeled accordingly and the list of whether each of the pawns has been placed with the correct adjustments (for pawns that were placed)
    if board_line[0] == '|':  # looking at the sample board provided, one notices that whenever line contains a regular (non-SpecialLocation) spot for pawns to possibly belong, the line starts with '|'
        pawn_index = 0
        for pawn_label in all_pawns:
            if isinstance(all_pawns[pawn_label], dict) and all_pawns[pawn_label][Coordinate.Y] == line_y_pos:
                board_line = board_line[:all_pawns[pawn_label][Coordinate.X] * 5 + 2] + pawn_label + board_line[all_pawns[pawn_label][Coordinate.X] * 5 + 2 + len(pawn_label):]
                is_which_pawns_placed[pawn_index] = True
            pawn_index += 1
    if any(element in board_line for element in ['/      \\', '\\      /', '|        |']):  # board_line contains a location a pawn in a SpecialLocation.START.value or SpecialLocation.HOME.value location may belong in
        start_of_substring_search_index = 0
        while board_line.find('/      \\', start_of_substring_search_index) != -1 or board_line.find('\\      /', start_of_substring_search_index) != -1:
            start_of_substring_search_index = max(board_line.find('/      \\', start_of_substring_search_index), board_line.find('\\      /', start_of_substring_search_index))  # looking at the sample board provided, one notices that '/      \\' and '\\      /' never both occur on the same line (therefore one of the find() will return -1 and the other whatever was found)
            length_of_found_string = len('/      \\')  # also equals len('\\      /')
            player_letter = None  # the first letter of the name of the player this special location belongs to
            special_location = None  # whether this special location is a start or home area
            if board_line[0] == '+':  # looking at the sample board provided, one notices that the presence of '+' or '-' on a line with '\\      /' or '/      \\' indicates the presence of a SpecialLocation for the red or yellow player, and furthermore that only the first character of the line need be compared to '+'
                if (start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 2) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 2) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 2:  # this special location is on the left half of the board (indicating being for either the green or yellow player)
                    player_letter = Color.YELLOW.name[0]
                    special_location = (SpecialLocation.START.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 4) else SpecialLocation.HOME.value)  # if this special location is in the first quartile (going left to right) of the board, then it is the yellow player's SpecialLocation.START.value, else it is in the second quartile (going left to right) of the board and hence is the yellow player's SpecialLocation.HOME.value
                else:  # this special location is on the right side of the board (indicating being for either the red or blue player)
                    player_letter = Color.RED.name[0]
                    special_location = (SpecialLocation.HOME.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - 3 * len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - 3 * len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < 3 * len(board_line) / 4) else SpecialLocation.START.value)  # if this special location is in the third quartile (going left to right) of the board, then it is the red player's SpecialLocation.HOME.value, else it is in the fourth quartile (going left to right) of the board and hence is the red player's SpecialLocation.START.value
            else:  # looking at the sample board provided, one notices that the lack of '+' or '-' on a line with '\\      /' or '/      \\' indicates the presence of a SpecialLocation for the green or blue player, and furthermore that only the first character of the line need be compared to '+'
                if (start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 2) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 2) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 2:  # this special location is on the left half of the board (indicating being for either the green or yellow player)
                    player_letter = Color.GREEN.name[0]
                    special_location = (SpecialLocation.HOME.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 4) else SpecialLocation.START.value)  # if this special location is in the first quartile (going left to right) of the board, then it is the green player's SpecialLocation.HOME.value, else it is in the second quartile (going left to right) of the board and hence is the green player's SpecialLocation.START.value
                else:  # this special location is on the right side of the board (indicating being for either the red or blue player)
                    player_letter = Color.BLUE.name[0]
                    special_location = (SpecialLocation.START.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - 3 * len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - 3 * len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < 3 * len(board_line) / 4) else SpecialLocation.HOME.value)  # if this special location is in the third quartile (going left to right) of the board, then it is the blue player's SpecialLocation.START.value, else it is in the fourth quartile (going left to right) of the board and hence is the blue player's SpecialLocation.HOME.value
            pawn_index = 0
            for pawn_label in all_pawns:
                if pawn_label[0] == player_letter and all_pawns[pawn_label] == special_location and not is_which_pawns_placed[pawn_index]:
                    board_line = board_line[:start_of_substring_search_index + 3] + pawn_label + board_line[start_of_substring_search_index + 3 + len(pawn_label):]
                    is_which_pawns_placed[pawn_index] = True
                    break  # no more all_pawns can fit in the special location on this line
                pawn_index += 1
            start_of_substring_search_index += length_of_found_string  # continue the search for special locations from beyond what was last found

        start_of_substring_search_index = 0
        while board_line.find('|        |', start_of_substring_search_index) != -1:
            start_of_substring_search_index = board_line.find('|        |', start_of_substring_search_index)
            length_of_found_string = len('|        |')
            is_a_slot_occupied = False
            player_letter = None  # the first letter of the name of the player this special location belongs to
            special_location = None  # whether this special location is a start or home area
            if board_line[0] == '+':  # looking at the sample board provided, one notices that the presence of '+' or '-' on a line with '|        |' indicates the presence of a SpecialLocation for the green or blue player, and furthermore that only the first character of the line need be compared to '+'
                if (start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 2) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 2) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 2:  # this special location is on the left half of the board (indicating being for either the green or yellow player)
                    player_letter = Color.GREEN.name[0]
                    special_location = (SpecialLocation.HOME.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 4) else SpecialLocation.START.value)  # if this special location is in the first quartile (going left to right) of the board, then it is the green player's SpecialLocation.HOME.value, else it is in the second quartile (going left to right) of the board and hence is the green player's SpecialLocation.START.value
                else:  # this special location is on the right side of the board (indicating being for either the red or blue player)
                    player_letter = Color.BLUE.name[0]
                    special_location = (SpecialLocation.START.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - 3 * len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - 3 * len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < 3 * len(board_line) / 4) else SpecialLocation.HOME.value)  # if this special location is in the third quartile (going left to right) of the board, then it is the blue player's SpecialLocation.START.value, else it is in the fourth quartile (going left to right) of the board and hence is the blue player's SpecialLocation.HOME.value
            else:  # looking at the sample board provided, one notices that the lack of '+' or '-' on a line with '|        |' indicates the presence of a SpecialLocation for the red or yellow player, and furthermore that only the first character of the line need be compared to '+'
                if (start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 2) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 2) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 2:  # this special location is on the left half of the board (indicating being for either the green or yellow player)
                    player_letter = Color.YELLOW.name[0]
                    special_location = (SpecialLocation.START.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < len(board_line) / 4) else SpecialLocation.HOME.value)  # if this special location is in the first quartile (going left to right) of the board, then it is the yellow player's SpecialLocation.START.value, else it is in the second quartile (going left to right) of the board and hence is the yellow player's SpecialLocation.HOME.value
                else:  # this special location is on the right side of the board (indicating being for either the red or blue player)
                    player_letter = Color.RED.name[0]
                    special_location = (SpecialLocation.HOME.value if ((start_of_substring_search_index if abs(start_of_substring_search_index - 3 * len(board_line) / 4) > abs(start_of_substring_search_index + length_of_found_string - 3 * len(board_line) / 4) else start_of_substring_search_index + length_of_found_string) < 3 * len(board_line) / 4) else SpecialLocation.START.value)  # if this special location is in the third quartile (going left to right) of the board, then it is the red player's SpecialLocation.HOME.value, else it is in the fourth quartile (going left to right) of the board and hence is the red player's SpecialLocation.START.value
            pawn_index = 0
            for pawn_label in all_pawns:
                if pawn_label[0] == player_letter and all_pawns[pawn_label] == special_location and not is_which_pawns_placed[pawn_index]:
                    board_line = board_line[:start_of_substring_search_index + 2 + 4 * is_a_slot_occupied] + pawn_label + board_line[start_of_substring_search_index + 2 + 4 * is_a_slot_occupied + len(pawn_label):]
                    is_which_pawns_placed[pawn_index] = True
                    if is_a_slot_occupied:  # no more pawns can fit in the special location on this line
                        break
                    is_a_slot_occupied = True
                pawn_index += 1
            start_of_substring_search_index += length_of_found_string  # continue the search for special locations from beyond what was last found

    if line_y_pos in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value]:
        board_line_with_slides_colored = ''
        character_being_colored = None
        for char in board_line:
            if character_being_colored is None and char in ['>', '<', '=', '0']:
                character_being_colored = char
                board_line_with_slides_colored += (Color.GREEN.value if line_y_pos == 0 else Color.BLUE.value)
            elif character_being_colored is not None and char != character_being_colored:
                character_being_colored = None
                board_line_with_slides_colored += Color.RESET.value
            board_line_with_slides_colored += char
        board_line = board_line_with_slides_colored
    else:
        if line_y_pos < int(Coordinate.MAX_Y.value / 2) + 1:
            board_line = board_line[:6] + Color.GREEN.value + board_line[6:int(len(board_line) / 2)] + Color.RESET.value + (board_line[int(len(board_line) / 2)] if len(board_line) % 2 == 1 else '') + Color.RED.value + board_line[int(len(board_line) / 2) + (len(board_line) % 2 == 1):len(board_line) - 6] + Color.RESET.value + board_line[len(board_line) - 6:]
        elif line_y_pos > int(Coordinate.MAX_Y.value / 2) + 1:
            board_line = board_line[:6] + Color.YELLOW.value + board_line[6:int(len(board_line) / 2)] + Color.RESET.value + (board_line[int(len(board_line) / 2)] if len(board_line) % 2 == 1 else '') + Color.BLUE.value + board_line[int(len(board_line) / 2) + (len(board_line) % 2 == 1):len(board_line) - 6] + Color.RESET.value + board_line[len(board_line) - 6:]
        else:  # line_y_pos == int(Coordinate.MAX_Y.value / 2) + 1
            board_line = board_line[:6] + Color.GREEN.value + board_line[6:int(len(board_line) / 2)] + Color.RESET.value + (board_line[int(len(board_line) / 2)] if len(board_line) % 2 == 1 else '') + Color.BLUE.value + board_line[int(len(board_line) / 2) + (len(board_line) % 2 == 1):len(board_line) - 6] + Color.RESET.value + board_line[len(board_line) - 6:]
        if board_line[0] == '|':
            board_line_with_slides_colored = board_line[0]
            character_being_colored = None
            for board_line_index in range(1, min(board_line.find('|\033[0;3', 1) if board_line.find('|\033[0;3', 1) != -1 else len(board_line), board_line.find('+', 1) if board_line.find('+', 1) != -1 else len(board_line))):
                if character_being_colored is None and board_line[board_line_index] in ['^', 'V', '|', '0']:
                    character_being_colored = board_line[board_line_index]
                    board_line_with_slides_colored += Color.YELLOW.value
                elif character_being_colored is not None and board_line[board_line_index] != character_being_colored:
                    character_being_colored = None
                    board_line_with_slides_colored += Color.RESET.value
                board_line_with_slides_colored += board_line[board_line_index]
            board_line_with_slides_colored += (Color.RESET.value if character_being_colored is not None and board_line[min(board_line.find('|\033[0;3', 1) if board_line.find('|\033[0;3', 1) != -1 else len(board_line), board_line.find('+', 1) if board_line.find('+', 1) != -1 else len(board_line))] != character_being_colored else '') + board_line[min(board_line.find('|\033[0;3', 1) if board_line.find('|\033[0;3', 1) != -1 else len(board_line), board_line.find('+', 1) if board_line.find('+', 1) != -1 else len(board_line)):max(board_line.rfind(Color.RESET.value + '|', 0, -1) + len(Color.RESET.value + '|') - 1, board_line.rfind('+', 0, -1) + len('+') - 1) + 1]
            character_being_colored = None  # reset
            for board_line_index in range(max(board_line.rfind(Color.RESET.value + '|', 0, -1) + len(Color.RESET.value + '|') - 1, board_line.rfind('+', 0, -1) + len('+') - 1) + 1 - len(board_line), -1):
                if character_being_colored is None and board_line[board_line_index] in ['^', 'V', '|', '0']:
                    character_being_colored = board_line[board_line_index]
                    board_line_with_slides_colored += Color.RED.value
                elif character_being_colored is not None and board_line[board_line_index] != character_being_colored:
                    character_being_colored = None
                    board_line_with_slides_colored += Color.RESET.value
                board_line_with_slides_colored += board_line[board_line_index]
            board_line_with_slides_colored += (Color.RESET.value if character_being_colored is not None and board_line[-1] != character_being_colored else '') + board_line[-1]
            board_line = board_line_with_slides_colored
    if board_line[0] == '|':
        for pawn_label in all_pawns:  # color pawns on the border
            pawn_color = get_text_color(pawn_label[0])
            if line_y_pos in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value]:
                board_line = board_line.replace(pawn_label, pawn_color + pawn_label + Color.RESET.value, 1)  # optional count parameter to replace() is provided in an attempt to speed it up as only one of each pawn label should appear on a given board line
            else:
                board_line = board_line[:board_line.find('|\033[0;3', 1)].replace(pawn_label, pawn_color + pawn_label + Color.RESET.value, 1) + board_line[board_line.find('|\033[0;3', 1):board_line.rfind(Color.RESET.value + '|', 0, -1) + len(Color.RESET.value + '|') - 1] + board_line[board_line.rfind(Color.RESET.value + '|', 0, -1) + len(Color.RESET.value + '|') - 1:].replace(pawn_label, pawn_color + pawn_label + Color.RESET.value, 1)  # optional count parameter to replace() are provided in an attempt to speed it up as only one of each pawn label should appear on a given board line
    return board_line


def print_board(all_pawns):
    is_which_pawns_placed = [False] * len(all_pawns)  # specifically for when a pawns' location is SpecialLocation.START.value or SpecialLocation.HOME.value
    board_line_num = 0
    print('+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+')
    board_line_num += 1
    print(format_board_line('|    |>>>>|====|====|0000|    |    |    |    |>>>>|====|====|====|0000|    |    |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print('+----+---++----++---+----+----+----+----+----+----+----+----+----+----+----+----+')
    board_line_num += 1
    print(format_board_line('|    |   ||    ||  /      \\                 ----                           |VVVV|', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+   ++----++ |        |              /      \\+====+====+====+====+====+----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|0000|   ||    ||  \\      /              |        |    |    |    |    |    | || |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+   ++----++    ----                 \\      /+====+====+====+====+====+----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('| || |   ||    ||                           ----                     ----  | || |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+   ++----++                                                  /      \\+----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('| || |   ||    ||                                                 |        |0000|', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+   ++----++                                                  \\      /+----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('| || |   ||    ||                                                    ----  |    |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+   ++----++                                                          +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|^^^^|   /      \\                                                          |    |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+  |        |                                                         +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|    |   \\      /                                                          |    |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+     ----                                                   ----     +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|    |                                                          /      \\   |    |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+                                                         |        |  +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|    |                                                          \\      /   |VVVV|', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+                                                          ++----++   +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|    |  ----                                                    ||    ||   | || |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+/      \\                                                  ++----++   +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|0000|        |                                                 ||    ||   | || |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+\\      /                                                  ++----++   +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('| || |  ----                     ----                           ||    ||   | || |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+====+====+====+====+====+/      \\                 ----    ++----++   +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('| || |    |    |    |    |    |        |              /      \\  ||    ||   |0000|', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('+----+====+====+====+====+====+\\      /              |        | ++----++   +----+', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print(format_board_line('|^^^^|                           ----                 \\      /  ||    ||   |    |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    board_line_num += 1
    print('+----+----+----+----+----+----+----+----+----+----+----+----+---++----++---+----+')
    board_line_num += 1
    print(format_board_line('|    |    |0000|====|====|====|<<<<|    |    |    |    |0000|====|====|<<<<|    |', int(board_line_num / 2), all_pawns, is_which_pawns_placed))
    # board_line_num += 1  # unused/unnecessary
    print('+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+')
    # board_line_num += 1  # unused/unnecessary

    # Sample printed (initial) board state:
    # +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
    # |    |>>>>|====|====|0000|    |    |    |    |>>>>|====|====|====|0000|    |    |
    # +----+---++----++---+----+----+----+----+----+----+----+----+----+----+----+----+
    # |    |   ||    ||  /  G1  \                 ----                           |VVVV|
    # +----+   ++----++ | G2  G3 |              /      \+====+====+====+====+====+----+
    # |0000|   ||    ||  \  G4  /              |        |    |    |    |    |    | || |
    # +----+   ++----++    ----                 \      /+====+====+====+====+====+----+
    # | || |   ||    ||                           ----                     ----  | || |
    # +----+   ++----++                                                  /  R1  \+----+
    # | || |   ||    ||                                                 | R2  R3 |0000|
    # +----+   ++----++                                                  \  R4  /+----+
    # | || |   ||    ||                                                    ----  |    |
    # +----+   ++----++                                                          +----+
    # |^^^^|   /      \                                                          |    |
    # +----+  |        |                                                         +----+
    # |    |   \      /                                                          |    |
    # +----+     ----                                                   ----     +----+
    # |    |                                                          /      \   |    |
    # +----+                                                         |        |  +----+
    # |    |                                                          \      /   |VVVV|
    # +----+                                                          ++----++   +----+
    # |    |  ----                                                    ||    ||   | || |
    # +----+/  Y1  \                                                  ++----++   +----+
    # |0000| Y2  Y3 |                                                 ||    ||   | || |
    # +----+\  Y4  /                                                  ++----++   +----+
    # | || |  ----                     ----                           ||    ||   | || |
    # +----+====+====+====+====+====+/      \                 ----    ++----++   +----+
    # | || |    |    |    |    |    |        |              /  B1  \  ||    ||   |0000|
    # +----+====+====+====+====+====+\      /              | B2  B3 | ++----++   +----+
    # |^^^^|                           ----                 \  B4  /  ||    ||   |    |
    # +----+----+----+----+----+----+----+----+----+----+----+----+---++----++---+----+
    # |    |    |0000|====|====|====|<<<<|    |    |    |    |0000|====|====|<<<<|    |
    # +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+


def print_current_gameboard(all_pawns):  # takes as input a dictionary mapping pawn labels to their present location
    print("State of the game board:")
    print_board(all_pawns)
    print()


def print_last_discard_pile(last_discard_pile):
    print(f"Last discard pile ({len(last_discard_pile)} card{'s' if len(last_discard_pile) != 1 else ''}):")
    print(*reversed(last_discard_pile))
    print()


def print_discard_pile(discard_pile):
    print(f"Discard pile ({len(discard_pile)} card{'s' if len(discard_pile) != 1 else ''}):")
    print(*reversed(discard_pile))
    print()


def print_hand_of_cards(player):
    print("Your cards in hand:")
    print(*player.cards_in_hand)


def draw_card(draw_pile, discard_pile, last_discard_pile, num_times_to_show_last_discard_pile, num_players):  # returns the drawn card and how many times to show the last discard pile; adjusts the provided draw pile and discard pile by shuffling the discard pile back into the draw pile as necessary; also updates the last discard pile
    if not draw_pile:
        draw_pile.extend(discard_pile)
        last_discard_pile.clear()
        last_discard_pile.extend(discard_pile)
        discard_pile.clear()
        random.shuffle(draw_pile)
        print("Shuffled discard pile back into the draw pile.")
    return draw_pile.pop(), (num_times_to_show_last_discard_pile if discard_pile else num_players - 1)  # num_players - 1 show as not to show the last discard pile to the player that played the last card into it


def get_teammate_letter(player_letter):  # returns an empty string on error
    if player_letter == Color.BLUE.name[0]:
        return Color.GREEN.name[0]
    elif player_letter == Color.GREEN.name[0]:
        return Color.BLUE.name[0]
    elif player_letter == Color.RED.name[0]:
        return Color.YELLOW.name[0]
    elif player_letter == Color.YELLOW.name[0]:
        return Color.RED.name[0]
    return ''


def bump_pawns_at_coordinates(all_pawns, coordinates):  # moves all pawns in all_pawns that are currently located at coordinates found in the coordinates list parameter (consisting of dictionaries of ordered (x, y) pairs) to their SpecialLocation.START.value location
    num_bumped_pawns = 0
    for pawn_label in all_pawns:
        if all_pawns[pawn_label] in coordinates:
            all_pawns[pawn_label] = SpecialLocation.START.value
            num_bumped_pawns += 1
            if num_bumped_pawns > len(coordinates):  # there can only be one pawn at any given regular location, however a buffer of one extra (> rather than ==) is given in case (as is the case) elsewhere in the program the bumping pawn is desired to be removed as well, to be corrected after the call to bump_pawns_at_coordinates()
                return


def get_element_to_access(array_to_access, access_array):
    element_to_retrieve = array_to_access
    for access_index in access_array:
        element_to_retrieve = element_to_retrieve[access_index]
    return element_to_retrieve


def binary_search(value_to_find, array_to_search, access_array=None):  # array_to_search is allowed to be an array of arrays, and hence access_array specifies how to reach the values to search between as which element in each array level (of array_to_search) to access to ultimately reach the elements to compare (see get_element_to_access())
    if not array_to_search:
        return None
    min_index = 0
    max_index = len(array_to_search)
    current_index = int((max_index - min_index) / 2)
    if access_array is None:
        access_array = []
    access_array.insert(0, current_index)  # first element must be the current index
    element_to_compare = get_element_to_access(array_to_search, access_array)
    while element_to_compare != value_to_find and min_index != max_index:
        if element_to_compare < value_to_find:
            min_index = current_index
        else:  # element_to_compare > value_to_find
            max_index = current_index
        current_index = int((max_index + min_index) / 2)
        access_array[0] = current_index  # update the current index in access_array
        element_to_compare = get_element_to_access(array_to_search, access_array)
    return current_index if min_index != max_index else None


def move_pawn(num_spaces, label_of_pawn_to_move, all_pawns, name_of_player_making_move=None):  # takes the number of spaces to move the pawn of label label_of_pawn_to_move and an adjusted dictionary of all the pawns (having moved bumped pawns back to their SpecialLocation.START.value); returns (if name_of_player_making_move is provided) whether the movement was valid
    is_movement_forward = (num_spaces > 0)
    while num_spaces != 0:
        if all_pawns[label_of_pawn_to_move] == SpecialLocation.HOME.value:
            if name_of_player_making_move is not None:
                return False
            return
        elif all_pawns[label_of_pawn_to_move] == SpecialLocation.START.value:  # note that movements from the SpecialLocation.START.value are accepted, but anticipate the movement to be nonnegative
            if label_of_pawn_to_move[0] == Color.GREEN.name[0]:
                all_pawns[label_of_pawn_to_move] = Location.GREEN_START_EXIT.value.copy()
            elif label_of_pawn_to_move[0] == Color.RED.name[0]:
                all_pawns[label_of_pawn_to_move] = Location.RED_START_EXIT.value.copy()
            elif label_of_pawn_to_move[0] == Color.YELLOW.name[0]:
                all_pawns[label_of_pawn_to_move] = Location.YELLOW_START_EXIT.value.copy()
            elif label_of_pawn_to_move[0] == Color.BLUE.name[0]:  # this last condition check is actually redundant
                all_pawns[label_of_pawn_to_move] = Location.BLUE_START_EXIT.value.copy()
            break  # no further movement is allowed if the pawn is moved from its start location
        elif all_pawns[label_of_pawn_to_move][Coordinate.X] not in [Coordinate.MIN_X.value, Coordinate.MAX_X.value] and all_pawns[label_of_pawn_to_move][Coordinate.Y] not in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value]:  # if in a safe zone
            if label_of_pawn_to_move[0] == Color.GREEN.name[0]:
                all_pawns[label_of_pawn_to_move][Coordinate.Y] += (1 if is_movement_forward else -1)
            elif label_of_pawn_to_move[0] == Color.RED.name[0]:
                all_pawns[label_of_pawn_to_move][Coordinate.X] += (-1 if is_movement_forward else 1)
            elif label_of_pawn_to_move[0] == Color.YELLOW.name[0]:
                all_pawns[label_of_pawn_to_move][Coordinate.X] += (1 if is_movement_forward else -1)
            elif label_of_pawn_to_move[0] == Color.BLUE.name[0]:  # this last condition check is actually redundant
                all_pawns[label_of_pawn_to_move][Coordinate.Y] += (-1 if is_movement_forward else 1)
            if all_pawns[label_of_pawn_to_move] in Location.HOME_COORDINATES.value:  # if at a SpecialLocation.HOME.value location
                all_pawns[label_of_pawn_to_move] = SpecialLocation.HOME.value
        elif all_pawns[label_of_pawn_to_move] == Location.GREEN_SAFETY_ZONE_ENTRANCE.value and label_of_pawn_to_move[0] == Color.GREEN.name[0]:  # if the pawn is green and at the entrance to the green player's safe zone
            all_pawns[label_of_pawn_to_move][Coordinate.Y if is_movement_forward else Coordinate.X] += (1 if is_movement_forward else -1)
        elif all_pawns[label_of_pawn_to_move] == Location.RED_SAFETY_ZONE_ENTRANCE.value and label_of_pawn_to_move[0] == Color.RED.name[0]:  # if the pawn is red and at the entrance to the red player's safe zone
            all_pawns[label_of_pawn_to_move][Coordinate.X if is_movement_forward else Coordinate.Y] += (-1 if is_movement_forward else 1)
        elif all_pawns[label_of_pawn_to_move] == Location.YELLOW_SAFETY_ZONE_ENTRANCE.value and label_of_pawn_to_move[0] == Color.YELLOW.name[0]:  # if the pawn is yellow and at the entrance to the yellow player's safe zone
            all_pawns[label_of_pawn_to_move][Coordinate.X if is_movement_forward else Coordinate.Y] += (1 if is_movement_forward else -1)
        elif all_pawns[label_of_pawn_to_move] == Location.BLUE_SAFETY_ZONE_ENTRANCE.value and label_of_pawn_to_move[0] == Color.BLUE.name[0]:  # if the pawn is blue and at the entrance to the blue player's safe zone
            all_pawns[label_of_pawn_to_move][Coordinate.Y if is_movement_forward else Coordinate.X] += (-1 if is_movement_forward else 1)
        elif all_pawns[label_of_pawn_to_move][Coordinate.X] not in [Coordinate.MIN_X.value, Coordinate.MAX_X.value] and all_pawns[label_of_pawn_to_move][Coordinate.Y] == Coordinate.MIN_Y.value:  # if pawn is on top edge of board
            all_pawns[label_of_pawn_to_move][Coordinate.X] += (1 if is_movement_forward else -1)
        elif all_pawns[label_of_pawn_to_move][Coordinate.X] not in [Coordinate.MIN_X.value, Coordinate.MAX_X.value] and all_pawns[label_of_pawn_to_move][Coordinate.Y] == Coordinate.MAX_Y.value:  # if pawn is on bottom edge of board
            all_pawns[label_of_pawn_to_move][Coordinate.X] -= (1 if is_movement_forward else -1)
        elif all_pawns[label_of_pawn_to_move][Coordinate.X] == Coordinate.MIN_X.value and all_pawns[label_of_pawn_to_move][Coordinate.Y] not in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value]:  # if pawn is on left edge of board
            all_pawns[label_of_pawn_to_move][Coordinate.Y] -= (1 if is_movement_forward else -1)
        elif all_pawns[label_of_pawn_to_move][Coordinate.X] == Coordinate.MAX_X.value and all_pawns[label_of_pawn_to_move][Coordinate.Y] not in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value]:  # if pawn is on right edge of board
            all_pawns[label_of_pawn_to_move][Coordinate.Y] += (1 if is_movement_forward else -1)
        elif all_pawns[label_of_pawn_to_move] == {Coordinate.X: 0, Coordinate.Y: 0}:  # if pawn is in the top left square
            all_pawns[label_of_pawn_to_move][(Coordinate.X if is_movement_forward else Coordinate.Y)] += 1
        elif all_pawns[label_of_pawn_to_move] == {Coordinate.X: 15, Coordinate.Y: 0}:  # if pawn is in the top right square
            all_pawns[label_of_pawn_to_move][(Coordinate.Y if is_movement_forward else Coordinate.X)] += (1 if is_movement_forward else -1)
        elif all_pawns[label_of_pawn_to_move] == {Coordinate.X: 0, Coordinate.Y: 15}:  # if pawn is in the bottom left square
            all_pawns[label_of_pawn_to_move][(Coordinate.Y if is_movement_forward else Coordinate.X)] += (-1 if is_movement_forward else 1)
        elif all_pawns[label_of_pawn_to_move] == {Coordinate.X: 15, Coordinate.Y: 15}:  # if pawn is in the bottom right square; this last condition check is actually redundant
            all_pawns[label_of_pawn_to_move][(Coordinate.X if is_movement_forward else Coordinate.Y)] -= 1
        num_spaces += (-1 if is_movement_forward else 1)
    if all_pawns[label_of_pawn_to_move] not in [SpecialLocation.START.value, SpecialLocation.HOME.value] and ((label_of_pawn_to_move[0] == Color.BLUE.name[0] and all_pawns[label_of_pawn_to_move][Coordinate.Y] != Coordinate.MAX_Y.value) or (label_of_pawn_to_move[0] == Color.GREEN.name[0] and all_pawns[label_of_pawn_to_move][Coordinate.Y] != Coordinate.MIN_Y.value) or (label_of_pawn_to_move[0] == Color.RED.name[0] and all_pawns[label_of_pawn_to_move][Coordinate.X] != Coordinate.MAX_X.value) or (label_of_pawn_to_move[0] == Color.YELLOW.name[0] and all_pawns[label_of_pawn_to_move][Coordinate.X] != Coordinate.MIN_X.value)):  # if not on line corresponding to pawn's color
        if all_pawns[label_of_pawn_to_move] in Location.SLIDE_ENTRANCES.value:  # if at the start of a slide
            this_slide_location = all_pawns[label_of_pawn_to_move][Coordinate.X] + all_pawns[label_of_pawn_to_move][Coordinate.Y]  # summing the x and y coordinates gives a unique sum for each slide, and hence is used to determine which slide is being ridden
            slide_locations = [[1, {Coordinate.X: 3}], [6, {Coordinate.Y: -4}], [9, {Coordinate.X: 4}], [14, {Coordinate.Y: -3}], [16, {Coordinate.Y: 3}], [21, {Coordinate.X: -4}], [24, {Coordinate.Y: 4}], [29, {Coordinate.X: -3}]]  # each index of slide_locations is the sum of the x and y coordinates of the start of the slide, followed by a dictionary of which coordinate of the pawn to update and by (adding) what amount
            this_slide_location_index = binary_search(this_slide_location, slide_locations, [0])
            slide_object = slide_locations[this_slide_location_index]
            coordinate_to_update = list(slide_object[1].keys())[0]
            saved_pawn_location = all_pawns[label_of_pawn_to_move].copy()  # save the location of where the moved pawn belongs as bump_pawns_at_coordinates() will indiscriminately send it back to SpecialLocation.START.value
            saved_pawn_location[coordinate_to_update] += slide_locations[this_slide_location_index][1][coordinate_to_update]  # save the location of where the moved pawn belongs as bump_pawns_at_coordinates() will indiscriminately send it back to SpecialLocation.START.value
            bump_pawns_at_coordinates(all_pawns, list(({Coordinate.X: x_value, Coordinate.Y: saved_pawn_location[Coordinate.Y]} for x_value in range(min(saved_pawn_location[Coordinate.X], all_pawns[label_of_pawn_to_move][Coordinate.X]), max(saved_pawn_location[Coordinate.X], all_pawns[label_of_pawn_to_move][Coordinate.X]) + 1)) if saved_pawn_location[Coordinate.Y] in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value] else ({Coordinate.X: saved_pawn_location[Coordinate.X], Coordinate.Y: y_value} for y_value in range(min(saved_pawn_location[Coordinate.Y], all_pawns[label_of_pawn_to_move][Coordinate.Y]), max(saved_pawn_location[Coordinate.Y], all_pawns[label_of_pawn_to_move][Coordinate.Y]) + 1))))
            all_pawns[label_of_pawn_to_move] = saved_pawn_location
            if name_of_player_making_move is not None:
                return True
            return
    is_bump_valid = True
    if all_pawns[label_of_pawn_to_move] != SpecialLocation.HOME.value:
        saved_pawn_location = all_pawns[label_of_pawn_to_move]  # save the location of where the moved pawn belongs as bump_pawns_at_coordinates() will indiscriminately send it back to SpecialLocation.START.value
        pawns_that_must_not_be_landed_on = {}  # pawns are forbidden from landing on pawns belonging to the player making the play
        if name_of_player_making_move is not None:
            for pawn_label in all_pawns:
                if pawn_label[0] == name_of_player_making_move[0] and pawn_label != label_of_pawn_to_move:
                    pawns_that_must_not_be_landed_on[pawn_label] = all_pawns[pawn_label]
        bump_pawns_at_coordinates(all_pawns, [all_pawns[label_of_pawn_to_move]])
        if name_of_player_making_move is not None:
            for pawn_label in all_pawns:
                if pawn_label in pawns_that_must_not_be_landed_on and pawns_that_must_not_be_landed_on[pawn_label] != all_pawns[pawn_label]:
                    is_bump_valid = False
        all_pawns[label_of_pawn_to_move] = saved_pawn_location
    if name_of_player_making_move is not None:
        return is_bump_valid


def is_valid_target(pawn_targets, card_value, name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, is_card_a_ten_as_backward_one):  # returns a boolean representing whether the given pawn collection can be targeted by the card in question (and given the card in question's function in the instance of a seven or ten - can_sevens_be_split_across_more_than_two_pawns is a boolean that is only used if the card is a seven and and is_card_a_ten_as_backward_one can be True, False, or None), knowing whose turn it is, the state of the board, whether there are teams, and all selected pawn targets of the card
    if 'd' in pawn_targets:  # the discarding action is presumed to already have been verified to be valid
        return len(pawn_targets) == 1
    if card_value in ['1', '2', '3', '5', '8', '10', '12'] or (card_value == '11' and len(pawn_targets) == 1):
        if len(pawn_targets) == 1:
            if (pawn_targets[0][0] == name_of_player_to_play[0] or (are_teams and pawn_targets[0][0] == get_teammate_letter(name_of_player_to_play[0]))) and all_pawns[pawn_targets[0]] != SpecialLocation.HOME.value and (all_pawns[pawn_targets[0]] != SpecialLocation.START.value or card_value in ['1', '2']):
                return move_pawn((int(card_value) if card_value != '10' or not is_card_a_ten_as_backward_one else -1), pawn_targets[0], copy.deepcopy(all_pawns), name_of_player_to_play)  # modified all_pawns parameter gets ignored
        # elif not pawn_targets and card_value == '2':  # is_valid_target() doesn't check for the card being a two with no movements
        #     return True  # is_valid_target() doesn't check for the card being a two with no movements
    elif card_value == '4':
        if len(pawn_targets) == 1:
            if (pawn_targets[0][0] == name_of_player_to_play[0] or (are_teams and pawn_targets[0][0] == get_teammate_letter(name_of_player_to_play[0]))) and all_pawns[pawn_targets[0]] not in [SpecialLocation.HOME.value, SpecialLocation.START.value]:
                return move_pawn(-4, pawn_targets[0], copy.deepcopy(all_pawns), name_of_player_to_play)  # modified all_pawns parameter gets ignored
    elif card_value == '7':
        if can_sevens_be_split_across_more_than_two_pawns or len(pawn_targets) <= 2:
            movement_sum = 0
            seen_pawn_labels = []  # keeps track of which pawn labels have been seen (and hence repeated)
            all_pawns_copy = copy.deepcopy(all_pawns)
            for pawn_label in pawn_targets:
                if all_pawns[pawn_label] in [SpecialLocation.START.value, SpecialLocation.HOME.value]:
                    return False
                if pawn_label in seen_pawn_labels:  # a pawn is not allowed to appear multiple times in pawn_targets
                    return False
                seen_pawn_labels.append(pawn_label)
                if pawn_label[0] != name_of_player_to_play[0] and (not are_teams or pawn_label[0] != get_teammate_letter(name_of_player_to_play[0])):
                    return False
                if not move_pawn(pawn_targets[pawn_label], pawn_label, all_pawns_copy, name_of_player_to_play):  # update local copy of all_pawns (all_pawns_copy) as it is not returned and to confirm simulated movements are consistent with each other
                    return False
                movement_sum += pawn_targets[pawn_label]
            return movement_sum == 7
    elif card_value == '11':  # already determined that len(pawn_targets) != 1
        if len(pawn_targets) == 2 and all_pawns[pawn_targets[0]] not in [SpecialLocation.START.value, SpecialLocation.HOME.value] and (all_pawns[pawn_targets[0]][Coordinate.X] in [Coordinate.MIN_X.value, Coordinate.MAX_X.value] or all_pawns[pawn_targets[0]][Coordinate.Y] in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value]) and all_pawns[pawn_targets[1]] not in [SpecialLocation.START.value, SpecialLocation.HOME.value] and (all_pawns[pawn_targets[1]][Coordinate.X] in [Coordinate.MIN_X.value, Coordinate.MAX_X.value] or all_pawns[pawn_targets[1]][Coordinate.Y] in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value]):
            return pawn_targets[0][0] != pawn_targets[1][0] and ((pawn_targets[0][0] != name_of_player_to_play[0] and (pawn_targets[1][0] == name_of_player_to_play[0] or (are_teams and pawn_targets[1][0] == get_teammate_letter(name_of_player_to_play[0])))) or (pawn_targets[1][0] != name_of_player_to_play[0] and (pawn_targets[0][0] == name_of_player_to_play[0] or (are_teams and pawn_targets[0][0] == get_teammate_letter(name_of_player_to_play[0])))))  # if one pawn target belongs to the current player's side and the other doesn't belong to the current player
    elif card_value == 'Sorry':
        if len(pawn_targets) == 2:
            if pawn_targets[0][0] != pawn_targets[1][0]:
                if pawn_targets[0][0] != name_of_player_to_play[0] and (pawn_targets[1][0] == name_of_player_to_play[0] or (are_teams and pawn_targets[1][0] == get_teammate_letter(name_of_player_to_play[0]))):  # if one pawn target belongs to the current player's side and the other doesn't belong to the current player
                    return all_pawns[pawn_targets[1]] == SpecialLocation.START.value and all_pawns[pawn_targets[0]] not in [SpecialLocation.START.value, SpecialLocation.HOME.value] and (all_pawns[pawn_targets[0]][Coordinate.X] in [Coordinate.MIN_X.value, Coordinate.MAX_X.value] or all_pawns[pawn_targets[0]][Coordinate.Y] in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value])
                elif pawn_targets[1][0] != name_of_player_to_play[0] and (pawn_targets[0][0] == name_of_player_to_play[0] or (are_teams and pawn_targets[0][0] == get_teammate_letter(name_of_player_to_play[0]))):  # if one pawn target belongs to the current player's side and the other doesn't belong to the current player
                    return all_pawns[pawn_targets[0]] == SpecialLocation.START.value and all_pawns[pawn_targets[1]] not in [SpecialLocation.START.value, SpecialLocation.HOME.value] and (all_pawns[pawn_targets[1]][Coordinate.X] in [Coordinate.MIN_X.value, Coordinate.MAX_X.value] or all_pawns[pawn_targets[1]][Coordinate.Y] in [Coordinate.MIN_Y.value, Coordinate.MAX_Y.value])
    return False


def is_some_valid_split_for_seven(pawn_targets, name_of_player_to_play, all_pawns, are_teams, seven_remaining_distance, can_sevens_be_split_across_more_than_two_pawns):  # card value is assumed to be '7'; returns a boolean
    if is_valid_target(pawn_targets, '7', name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, False):  # if valid as is (particularly used during recursion)
        return True
    for pawn_label in all_pawns:
        if (pawn_label[0] == name_of_player_to_play[0] or (are_teams and pawn_label[0] == get_teammate_letter(name_of_player_to_play[0]))) and not any(pawn_label in pawn_target for pawn_target in pawn_targets):
            for movement_distance in range(seven_remaining_distance + 1, 1, -1):  # decrementing should find a valid move (if one exists) sooner than incrementing as incrementing will most often require recursion
                pawn_targets[pawn_label] = movement_distance
                if is_some_valid_split_for_seven(pawn_targets, name_of_player_to_play, all_pawns, are_teams, seven_remaining_distance - movement_distance, can_sevens_be_split_across_more_than_two_pawns):  # as recursion may be required to find a valid move
                    pawn_targets.pop(pawn_label)  # de-modify pawn_targets before returning
                    return True
                pawn_targets.pop(pawn_label)  # remove attempt from pawn_targets
    return False


def is_some_valid_move_for_ten(pawn_targets, name_of_player_to_play, all_pawns, are_teams):  # card value is assumed to be '10'; returns a boolean
    return is_valid_target(pawn_targets, '10', name_of_player_to_play, all_pawns, are_teams, None, True) or is_valid_target(pawn_targets, '10', name_of_player_to_play, all_pawns, are_teams, None, False)


def is_some_valid_swap_for_eleven(existing_pawn_target, name_of_player_to_play, all_pawns, are_teams):  # card value is assumed to be '11'; returns a boolean
    for pawn_label in all_pawns:
        if pawn_label != existing_pawn_target and is_valid_target([existing_pawn_target, pawn_label], '11', name_of_player_to_play, all_pawns, are_teams, None, False):
            return True
    return False


def is_some_valid_play_for_sorry(existing_pawn_target, name_of_player_to_play, all_pawns, are_teams):  # card value is assumed to be 'Sorry'; returns a boolean
    for pawn_label in all_pawns:
        if pawn_label != existing_pawn_target and is_valid_target([existing_pawn_target, pawn_label], 'Sorry', name_of_player_to_play, all_pawns, are_teams, None, False):
            return True
    return False


def add_play_score_attribute(play, hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile):  # adds a 'play_score' attribute with a corresponding score to the play dictionary parameter according to the estimated value of executing the play using the rest of the parameters
    play['play_score'] = random.randrange(100)  # primitive (random) solution  # TODO: better scoring heuristics


def enumerate_possible_plays(hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile=None):  # hand_of_cards is required as valid moves (e.g. discarding is only allowed when the only other valid play is playing an eleven as a swap) depend on other whether other cards have moves; do_return_whether_is_some is a boolean representing whether (if True) to return whether there is at least one valid play instead of returning an array of the enumerated valid plays; the presence of discard_pile parameter indicates to score each possible play (for a computer-controlled player)
    possible_plays = []  # an array containing dictionaries of the (first) card to play (card_to_play), an array of any and all pawn targets (pawn_targets) called for by the play, (if discard_pile is not None and not do_return_whether_is_some) a score (play_score) of the play, and (if the card to play is a ten) a boolean (is_card_a_ten_as_backward_one) specifying to use the ten to move a/the pawn backwards by one
    for card in hand_of_cards:
        if card in ['1', '2', '3', '4', '5', '8', '11', '12']:
            for pawn_label in all_pawns:
                if is_valid_target([pawn_label], card, name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, None):
                    if do_return_whether_is_some:
                        return True
                    possible_plays.append({'card_to_play': card, 'pawn_targets': [pawn_label]})
                    add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
            if card == '2':
                can_2_validly_move_some_pawn = False  # to be corrected as necessary
                for possible_play in reversed(possible_plays):  # reversed possible_plays to improve time complexity as really only the last/latest element of possible_plays should be checked for 'card_to_play' equaling '2'
                    if possible_play['card_to_play'] == '2':
                        can_2_validly_move_some_pawn = True
                        break
                if not can_2_validly_move_some_pawn and (not is_immediate_draw_after_playing_a_2 or len(hand_of_cards) > 1):  # notably, having a '2' in hand leads to always having a viable play, unless playing a '2' requires a follow-up card to be played (as is expected), but the player won't have any card to possibly follow-up with
                    if do_return_whether_is_some:
                        return True
                    possible_plays.append({'card_to_play': card, 'pawn_targets': []})  # playing a 2 purely as a draw (without moving a pawn and hence an empty pawn_targets array) is a valid play if and only if the 2 cannot validly move a pawn
                    add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
            elif card == '11':
                for pawn_label_1 in all_pawns:
                    for pawn_label_2 in all_pawns:
                        if is_valid_target([pawn_label_1, pawn_label_2], card, name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, None):
                            if do_return_whether_is_some:
                                return True
                            possible_plays.append({'card_to_play': card, 'pawn_targets': [pawn_label_1, pawn_label_2]})
                            add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
        elif card == '7':
            if can_sevens_be_split_across_more_than_two_pawns:
                pawn_indices = [0] * int(card)  # the indices of the pawns in movable_pawns to assign each movement distance to (for a total distance of seven)
                movable_pawns = []
                for pawn_label in all_pawns:
                    if (pawn_label[0] == name_of_player_to_play[0] or (are_teams and pawn_label[0] == get_teammate_letter(name_of_player_to_play[0]))) and all_pawns[pawn_label] not in [SpecialLocation.START.value, SpecialLocation.HOME.value]:
                        movable_pawns.append(pawn_label)
                while pawn_indices[len(pawn_indices) - 1] != int(card):
                    pawn_targets = {}
                    for i in range(len(movable_pawns)):
                        if pawn_indices.count(i) != 0:
                            pawn_targets[movable_pawns[i]] = pawn_indices.count(i)
                    possible_plays.append({'card_to_play': card, 'pawn_targets': pawn_targets})  # note that duplicate possible_plays entries will be generated
                    if not is_valid_target(possible_plays[len(possible_plays) - 1]['pawn_targets'], card, name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, None):  # remove the possible play if it is invalid
                        possible_plays.pop()
                    else:
                        add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
                    pawn_indices[0] += 1
                    for i in range(len(pawn_indices) - 1):
                        if pawn_indices[i] == len(movable_pawns):
                            pawn_indices[i] = 0  # reset index/counter
                            pawn_indices[i + 1] += 1  # increment next index/counter over
            else:
                movable_pawns = []
                for pawn_label in all_pawns:
                    if (pawn_label[0] == name_of_player_to_play[0] or (are_teams and pawn_label[0] == get_teammate_letter(name_of_player_to_play[0]))) and all_pawns[pawn_label] not in [SpecialLocation.START.value, SpecialLocation.HOME.value]:
                        movable_pawns.append(pawn_label)
                for movable_pawns_index_1 in range(len(movable_pawns)):
                    possible_plays.append({'card_to_play': card, 'pawn_targets': {movable_pawns[movable_pawns_index_1]: int(card)}})
                    if not is_valid_target(possible_plays[len(possible_plays) - 1]['pawn_targets'], card, name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, None):  # remove the possible play if it is invalid
                        possible_plays.pop()
                    else:
                        add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
                    for movement_count in range(1, int(card)):
                        for movable_pawns_index_2 in range(len(movable_pawns)):
                            possible_plays.append({'card_to_play': card, 'pawn_targets': {movable_pawns[movable_pawns_index_1]: movement_count}})
                            if movable_pawns_index_1 != movable_pawns_index_2:
                                possible_plays[len(possible_plays) - 1]['pawn_targets'][movable_pawns[movable_pawns_index_2]] = int(card) - movement_count
                            if not is_valid_target(possible_plays[len(possible_plays) - 1]['pawn_targets'], card, name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, None):  # remove the possible play if it is invalid
                                possible_plays.pop()
                            else:
                                add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
        elif card == '10':
            for pawn_label in all_pawns:
                if is_valid_target([pawn_label], card, name_of_player_to_play, all_pawns, are_teams, None, True):
                    if do_return_whether_is_some:
                        return True
                    possible_plays.append({'card_to_play': card, 'pawn_targets': [pawn_label], 'is_card_a_ten_as_backward_one': True})
                    add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
                if is_valid_target([pawn_label], card, name_of_player_to_play, all_pawns, are_teams, None, False):
                    if do_return_whether_is_some:
                        return True
                    possible_plays.append({'card_to_play': card, 'pawn_targets': [pawn_label], 'is_card_a_ten_as_backward_one': False})
                    add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
        elif card == 'Sorry':
            for pawn_label_1 in all_pawns:
                for pawn_label_2 in all_pawns:
                    if is_valid_target([pawn_label_1, pawn_label_2], card, name_of_player_to_play, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, None):
                        if do_return_whether_is_some:
                            return True
                        possible_plays.append({'card_to_play': card, 'pawn_targets': [pawn_label_1, pawn_label_2]})
                        add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
    is_only_valid_plays_eleven_as_swap = True  # to be corrected as necessary
    for possible_play in possible_plays:
        if possible_play['card_to_play'] != '11' or len(possible_play['pawn_targets']) != 2:
            is_only_valid_plays_eleven_as_swap = False
            break
    if do_return_whether_is_some:
        return possible_plays and not is_only_valid_plays_eleven_as_swap  # do_return_whether_is_some leads to returning False if only playable move is an eleven as swap since that is the only valid move that is permitted to be ignored and enumerate_possible_plays() with the do_return_whether_is_some is used to determine if discarding is allowed
    if not possible_plays or is_only_valid_plays_eleven_as_swap:  # discarding is only an option if there are no valid plays other than possibly using an eleven as a swap
        for card in hand_of_cards:
            possible_plays.append({'card_to_play': card, 'pawn_targets': ['d']})
            add_play_score_attribute(possible_plays[len(possible_plays) - 1], hand_of_cards, name_of_player_to_play, all_pawns, are_teams, do_return_whether_is_some, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
    return possible_plays


def determine_default_action(card_value, other_chosen_pawn_targets, all_possible_plays, all_pawns, name_of_player_making_play, are_teams):  # takes the already selected pawn targets (if existent), card, available/possible plays, the positions of every pawn (used if the card is a '1', '2', or 'Sorry' to determine which (if any) pawn would be moved from SpecialLocation.START.value and which (if any) pawn would be moved to SpecialLocation.START.value in generating the string explaining the default action), the name of the player making the play (used if the card is an '11' to determine if the first targeted pawn belongs to the player making the play (where hence the default action should be to move that pawn forward) or not (where hence the default action should be to swap with a friendly pawn if there is only one friendly pawn available to swap with)), and whether there are teams; (if only one valid pawn choice (including no pawns) exists for the given card to play and any pawn(s) selected) returns the remaining pawn target(s) of that choice, 'd' for discard, or None otherwise, and also returns a string to show the user to explain the default choice in more detail; requires card and pawn choices to be at least a part of some valid/possible play
    num_possible_plays_with_selections = 0
    default_action = []  # return no additional pawn targets if default choice is to use the '11' as a forward movement of a single pawn
    is_card_a_ten_as_backward_one = None
    if card_value != '11' or not other_chosen_pawn_targets or (other_chosen_pawn_targets[0][0] != name_of_player_making_play[0] and (not are_teams or other_chosen_pawn_targets[0][0] != get_teammate_letter(name_of_player_making_play[0]))):  # otherwise default action is to be playing the '11' as is (moving one pawn forward eleven spaces)
        if card_value != '7' and (card_value not in ['11', 'Sorry'] or other_chosen_pawn_targets):  # if order of pawn targets doesn't matter and card is not a 'Sorry' nor '11' with no pawn targets chosen yet
            for possible_play in all_possible_plays:
                if possible_play['card_to_play'] == card_value:
                    is_this_possible_play_an_option = True  # to be corrected as necessary
                    for pawn_target in other_chosen_pawn_targets:
                        if pawn_target not in possible_play['pawn_targets']:
                            is_this_possible_play_an_option = False
                            break
                    if num_possible_plays_with_selections != 0:  # if some default play has already been determined
                        if len(default_action) + len(other_chosen_pawn_targets) == len(possible_play['pawn_targets']):  # if the default play and this new possible play may be equivalent
                            is_play_equivalent = True  # to be corrected as necessary
                            for pawn_target in possible_play['pawn_targets']:
                                if pawn_target not in other_chosen_pawn_targets and pawn_target not in default_action:
                                    is_play_equivalent = False
                            if is_play_equivalent:
                                if card_value == '10' and default_action and is_card_a_ten_as_backward_one != possible_play['is_card_a_ten_as_backward_one']:
                                    is_card_a_ten_as_backward_one = None
                                is_this_possible_play_an_option = False  # equivalent plays are disregarded
                    if is_this_possible_play_an_option:
                        num_possible_plays_with_selections += 1
                        if num_possible_plays_with_selections != 1:  # if there are multiple possible plays knowing the chosen card and existing pawn choices
                            return None, ""
                        if card_value == '10' and 'is_card_a_ten_as_backward_one' in possible_play:
                            is_card_a_ten_as_backward_one = possible_play['is_card_a_ten_as_backward_one']
                        default_action = copy.deepcopy(possible_play['pawn_targets'])
                        for pawn_target in other_chosen_pawn_targets:
                            default_action.remove(pawn_target)  # remove existing pawn targets from pawn targets to add
        elif card_value in ['11', 'Sorry']:  # '11's and 'Sorry's (with no chosen pawn targets yet) are handled separately as a default first pawn choice may present itself (if there is only one friendly pawn in home or only one opponent pawn that could be bumped)
            for possible_play in all_possible_plays:
                if possible_play['card_to_play'] == card_value:
                    num_possible_plays_with_selections += 1
                    if num_possible_plays_with_selections == 1:
                        default_action += copy.deepcopy(possible_play['pawn_targets'])  # to be corrected as necessary (there are no other_chosen_pawn_targets to immediately remove)
                    else:
                        for possible_pawn_target in default_action:
                            if possible_pawn_target not in possible_play['pawn_targets']:  # to be a valid default pawn target, the pawn must appear in all possible plays
                                default_action.remove(possible_pawn_target)
            if not default_action:
                return None, ""
        else:  # order of pawn targets does matter
            for possible_play in all_possible_plays:
                if possible_play['card_to_play'] == card_value:
                    is_this_possible_play_an_option = True  # to be corrected as necessary
                    for i in range(len(other_chosen_pawn_targets)):  # .items() is left out in case other_chosen_pawn_targets is empty
                        if list(other_chosen_pawn_targets.items())[i] != list(possible_play['pawn_targets'].items())[i]:
                            is_this_possible_play_an_option = False
                            break
                    if num_possible_plays_with_selections != 0:  # if some default play has already been determined
                        if len(default_action) + len(other_chosen_pawn_targets) == len(possible_play['pawn_targets']):  # if the default play and this new possible play may be equivalent
                            is_play_equivalent = True  # to be corrected as necessary
                            for i in range(len(possible_play['pawn_targets'])):
                                if (list(possible_play['pawn_targets'].items())[i] if isinstance(possible_play['pawn_targets'], dict) else possible_play['pawn_targets'][i]) != (list(other_chosen_pawn_targets.items())[i] if i < len(other_chosen_pawn_targets) else (list(default_action.items())[i - len(other_chosen_pawn_targets)]) if isinstance(default_action, dict) else default_action[i - len(other_chosen_pawn_targets)]):  # possible_play['pawn_targets'] may be a list even for a '7' if it regards discarding; default_action may be a list even for a '7' if it regards discarding
                                    is_play_equivalent = False
                            if is_play_equivalent:
                                is_this_possible_play_an_option = False  # equivalent plays are disregarded
                    if is_this_possible_play_an_option:
                        num_possible_plays_with_selections += 1
                        if num_possible_plays_with_selections != 1:  # if there are multiple possible plays knowing the chosen card and existing pawn choices
                            return None, ""
                        default_action = (dict(list(possible_play['pawn_targets'].items())[len(other_chosen_pawn_targets):]) if isinstance(possible_play['pawn_targets'], dict) else possible_play['pawn_targets'][len(other_chosen_pawn_targets):])  # possible_play['pawn_targets'] may be a list even for a '7' if it regards discarding; default_action may be a list even for a '7' if it regards discarding
        if 'd' in default_action:
            return default_action, f"discarding this {card_value}"
    explanation_string = ""
    if card_value != '10' and (card_value != '11' or len(other_chosen_pawn_targets) + len(default_action) == 1) and card_value != 'Sorry':
        if default_action:
            for i in range(len(default_action)):
                explanation_string += f"moving pawn {default_action[i] if not isinstance(default_action, dict) else list(default_action.keys())[i]} "
                if all_pawns[(default_action[i] if not isinstance(default_action, dict) else list(default_action.keys())[i])] == SpecialLocation.START.value:
                    explanation_string += "from start"
                else:
                    explanation_string += f"{'for' if card_value != '4' and (card_value != '10' or not is_card_a_ten_as_backward_one) else 'back'}ward by {(int(card_value) if not is_card_a_ten_as_backward_one else 1) if not isinstance(default_action, dict) else list(default_action.values())[i]}{' then ' if i != len(default_action) - 1 else ''}"
        else:
            if card_value == '11':  # also len(other_chosen_pawn_targets) == 1 since it was confirmed the sum of len(other_chosen_pawn_targets) and len(default_action) was 1 but len(default_action) == 0
                explanation_string += f"moving pawn {other_chosen_pawn_targets[0]} forward by {int(card_value)}"
            # elif card_value == '2':  # also len(other_chosen_pawn_targets) == 0 as a '2' is the only card that could end up with no default action pawn picks while being given the option to pick more pawn targets  # deprecated for the user specifying to use the '2' only to draw being handled elsewhere
            #     explanation_string = "drawing a card without moving any pawn"  # deprecated for the user specifying to use the '2' only to draw being handled elsewhere
    elif card_value == '10':
        explanation_string += f"moving pawn {default_action[0]}"
        if is_card_a_ten_as_backward_one is not None:
            explanation_string += f" {'for' if not is_card_a_ten_as_backward_one else 'back'}ward by {int(card_value) if not is_card_a_ten_as_backward_one else 1}"
    elif card_value == '11':
        explanation_string = f"swapping the locations of pawns {default_action[0] if len(default_action) == 2 else other_chosen_pawn_targets[0]} and {default_action[len(default_action) - 1]}"
    elif card_value == 'Sorry':  # this last condition check is actually redundant
        pawn_in_start = None  # the label of the pawn determined to be at its start location (according the play to be valid)
        pawn_to_move_to_start = None  # the label of the pawn determined to not be at its start location (knowing the play to be valid)
        if other_chosen_pawn_targets:
            if other_chosen_pawn_targets[0][0] == name_of_player_making_play[0]:
                pawn_in_start = other_chosen_pawn_targets[0]
                pawn_to_move_to_start = default_action[0]
            elif default_action[0][0] == name_of_player_making_play[0]:
                pawn_in_start = default_action[0]
                pawn_to_move_to_start = other_chosen_pawn_targets[0]
            elif other_chosen_pawn_targets[0][0] == get_teammate_letter(name_of_player_making_play[0]):
                pawn_in_start = other_chosen_pawn_targets[0]
                pawn_to_move_to_start = default_action[0]
            elif default_action[0] == get_teammate_letter(name_of_player_making_play[0]):  # this last condition check is actually redundant
                pawn_in_start = default_action[0]
                pawn_to_move_to_start = other_chosen_pawn_targets[0]
        else:
            if all_pawns[default_action[0]] == SpecialLocation.START.value:
                pawn_in_start = default_action[0]
                if len(default_action) == 2:
                    pawn_to_move_to_start = default_action[1]  # because the possible/default play must be valid, for a 'Sorry', one of the pawn targets must be at SpecialLocation.START.value and the other not at SpecialLocation.START.value
            else:  # because the possible/default play must be valid, for a 'Sorry', one of the pawn targets must be at SpecialLocation.START.value and the other not at SpecialLocation.START.value
                if len(default_action) == 2:
                    pawn_in_start = default_action[1]
                pawn_to_move_to_start = default_action[0]
        explanation_string = f"putting {'some ' if pawn_in_start is None else ''}pawn {pawn_in_start + ' ' if pawn_in_start is not None else ''}in the place occupied by {pawn_to_move_to_start if pawn_to_move_to_start is not None else 'some other pawn'} and sending {'that other ' if pawn_to_move_to_start is None else ''}pawn {pawn_to_move_to_start + ' ' if pawn_to_move_to_start is not None else ''}back to its start"  # utilizes the knowledge of where the pawns are (all_pawns parameter) and the length of default_action to determine which pawn would be moved from SpecialLocation.START.value and which pawn would be moved to SpecialLocation.START.value
    return default_action, explanation_string


def play_card(card_to_play, pawn_targets, all_pawns, is_card_a_ten_as_backward_one=False):  # takes the card to play, a list of all the (labels of the) pawns to target (alternatively a dictionary of all the labels of the pawns to target mapped to how much to move each for the card 7), a to-be-adjusted dictionary of all the existing pawns, and (optionally) a flag indicating to treat the card (which must be a ten, but is not verified) as a movement backward by one; behavior is undefined if the play is invalid (see is_valid_target()) including if excessive or not enough pawn targets are provided
    if card_to_play in ['1', '2'] and all_pawns[pawn_targets[0]] == SpecialLocation.START.value:
        if pawn_targets[0][0] == Color.BLUE.name[0]:
            bump_pawns_at_coordinates(all_pawns, [Location.BLUE_START_EXIT.value])
            all_pawns[pawn_targets[0]] = Location.BLUE_START_EXIT.value.copy()
        elif pawn_targets[0][0] == Color.GREEN.name[0]:
            bump_pawns_at_coordinates(all_pawns, [Location.GREEN_START_EXIT.value])
            all_pawns[pawn_targets[0]] = Location.GREEN_START_EXIT.value.copy()
        elif pawn_targets[0][0] == Color.RED.name[0]:
            bump_pawns_at_coordinates(all_pawns, [Location.RED_START_EXIT.value])
            all_pawns[pawn_targets[0]] = Location.RED_START_EXIT.value.copy()
        elif pawn_targets[0][0] == Color.YELLOW.name[0]:
            bump_pawns_at_coordinates(all_pawns, [Location.YELLOW_START_EXIT.value])
            all_pawns[pawn_targets[0]] = Location.YELLOW_START_EXIT.value.copy()
    elif card_to_play == '7':
        for pawn_label in pawn_targets:
            move_pawn(pawn_targets[pawn_label], pawn_label, all_pawns)
    elif card_to_play == 'Sorry' or (card_to_play == '11' and len(pawn_targets) == 2):
        all_pawns[pawn_targets[0]], all_pawns[pawn_targets[1]] = all_pawns[pawn_targets[1]], all_pawns[pawn_targets[0]]
        if all_pawns[pawn_targets[0]] != SpecialLocation.START.value:
            move_pawn(0, pawn_targets[0], all_pawns)  # simulate a movement of zero to adjust in case an arrow was landed on
        if all_pawns[pawn_targets[1]] != SpecialLocation.START.value:
            move_pawn(0, pawn_targets[1], all_pawns)  # simulate a movement of zero to adjust in case an arrow was landed on
    elif card_to_play == '4' or is_card_a_ten_as_backward_one:
        move_pawn((-4 if not is_card_a_ten_as_backward_one else -1), pawn_targets[0], all_pawns)
    elif card_to_play in ['1', '2', '3', '5', '8', '10', '11', '12']:
        move_pawn(int(card_to_play), pawn_targets[0], all_pawns)


def get_player_type(player_name, default_enum):  # takes the player's name (as a string) and an enum mapping the word to show to indicate the default option to the value to assign if the default option is chosen; returns the selected PlayerType
    player_type = None
    while player_type is None or (player_type and player_type not in [PlayerType.COMPUTER.value, PlayerType.HUMAN.value, PlayerType.NONEXISTENT.value]):
        player_type = input(f"Is {get_text_color(player_name[0].upper())}{player_name}{Color.RESET.value} a computer ({PlayerType.COMPUTER.value}) or human ({PlayerType.HUMAN.value}) player or nonexistent ({PlayerType.NONEXISTENT.value})? (default is {default_enum.name.lower()}) ")
    if player_type == PlayerType.COMPUTER.value:
        player_type = PlayerType.COMPUTER
    elif player_type == PlayerType.HUMAN.value:
        player_type = PlayerType.HUMAN
    elif player_type == PlayerType.NONEXISTENT.value:
        player_type = PlayerType.NONEXISTENT
    return player_type if player_type else default_enum


def get_user_confirmation(message):  # returns True on confirmation and False on denial
    valid_confirmation_strings = ['y', 'yes']   # the first element of valid_confirmation_strings is shown in the prompt
    valid_denial_strings = ['n', 'no']   # the first element of valid_confirmation_strings is shown in the prompt
    input_string = None
    while input_string not in valid_confirmation_strings and input_string not in valid_denial_strings:
        input_string = input(f"{message} ({valid_confirmation_strings[0]}/{valid_denial_strings[0]}) ").strip().lower()
    return input_string in valid_confirmation_strings


def sorry_boardgame():  # returns zero on success and nonzero (some other integer) on failure
    num_players = 0
    blue_player_type = get_player_type(Color.BLUE.name.lower(), PlayerType.HUMAN)
    num_players += (blue_player_type != PlayerType.NONEXISTENT)
    green_player_type = get_player_type(Color.GREEN.name.lower(), PlayerType.COMPUTER)
    num_players += (green_player_type != PlayerType.NONEXISTENT)
    red_player_type = get_player_type(Color.RED.name.lower(), PlayerType.NONEXISTENT)
    num_players += (red_player_type != PlayerType.NONEXISTENT)
    yellow_player_type = get_player_type(Color.YELLOW.name.lower(), PlayerType.NONEXISTENT)
    num_players += (yellow_player_type != PlayerType.NONEXISTENT)
    print()

    are_teams = False   # teaming is only allowed in four-player games
    can_sevens_be_split_across_more_than_two_pawns = False   # the ability to split sevens among more than two pawns is only allowed in four-player games
    # if num_players == 0:  # deprecated for being excessively strict an unclear as to whether the the program should exit with or without an error code
        # return 1  # deprecated for being excessively strict an unclear as to whether the the program should exit with or without an error code
    if num_players == 1:
        if not get_user_confirmation("There is only one player. Are you sure you want to continue?"):
            return 0
    elif num_players == 4:
        are_teams = get_user_confirmation("Is play in teams?")
        if are_teams:
            can_sevens_be_split_across_more_than_two_pawns = get_user_confirmation("Can sevens be split across more than two pawns?")

    draw_pile = ['1'] * 5 + ['2'] * 4 + ['3'] * 4 + ['4'] * 4 + ['5'] * 4 + ['7'] * 4 + ['8'] * 4 + ['10'] * 4 + ['11'] * 4 + ['12'] * 4 + ['Sorry'] * 4  # distribution collected from an owned version of the game  # must have more cards than hand_size * num_players to begin with (to be able to deal)
    hand_size = None
    while hand_size is None or not isinstance(hand_size, int) or hand_size < 0 or hand_size > len(draw_pile) / num_players:
        hand_size = input("Hand size (default is 5): ")
        try:
            hand_size = int(hand_size)
        except ValueError:
            if not hand_size:
                hand_size = 5
    is_immediate_draw_after_playing_a_2 = (hand_size == 0) or get_user_confirmation("Can players immediately draw after playing a 2?")
    is_card_after_playing_a_2_force_played = is_immediate_draw_after_playing_a_2 and (hand_size == 0 or get_user_confirmation("Must players play the card they just drew after playing a 2?"))

    players = []  # blue, yellow, green, red (in order of play)
    if blue_player_type != PlayerType.NONEXISTENT:
        players.append(Player(Color.BLUE, blue_player_type, hand_size))
    if yellow_player_type != PlayerType.NONEXISTENT:
        players.append(Player(Color.YELLOW, yellow_player_type, hand_size))
    if green_player_type != PlayerType.NONEXISTENT:
        players.append(Player(Color.GREEN, green_player_type, hand_size))
    if red_player_type != PlayerType.NONEXISTENT:
        players.append(Player(Color.RED, red_player_type, hand_size))
    if get_user_confirmation("Faster play (each player begins the game with one pawn out of start)?"):
        for player in players:
            if player.name[0] == Color.BLUE.name[0]:
                player.pawns[player.name[0] + '1'] = Location.BLUE_START_EXIT.value.copy()
            elif player.name[0] == Color.GREEN.name[0]:
                player.pawns[player.name[0] + '1'] = Location.GREEN_START_EXIT.value.copy()
            elif player.name[0] == Color.RED.name[0]:
                player.pawns[player.name[0] + '1'] = Location.RED_START_EXIT.value.copy()
            elif player.name[0] == Color.YELLOW.name[0]:  # this last condition check is actually redundant
                player.pawns[player.name[0] + '1'] = Location.YELLOW_START_EXIT.value.copy()
    do_show_card_descriptions = get_user_confirmation(f"Turn on card descriptions during play (recommended with novice players)?")
    print()

    for player in players:
        if player.player_type != PlayerType.NONEXISTENT:
            print(f"{get_text_color(player.name[0])}{player.name}{Color.RESET.value} is", (PlayerType.COMPUTER.name.lower() if player.player_type == PlayerType.COMPUTER else PlayerType.HUMAN.name.lower()) + "-controlled")

    discard_pile = []
    random.shuffle(draw_pile)
    last_discard_pile = discard_pile.copy()  # to show the other players what was played just before the discard pile got reshuffled in case the pile was (re)shuffled since the player last saw it (to know what the other players played)
    num_times_to_show_last_discard_pile = 0  # for showing the other players what was played just before the discard pile got reshuffled in case the pile was (re)shuffled since the player last saw it (to know what the other players played)
    players_turn = random.randrange(num_players)
    input(f"{get_text_color(players[players_turn].name[0])}{players[players_turn].name}{Color.RESET.value} (randomly) goes first! Press enter to begin the game.")  # input() rather than print() so the console can immediately be cleared afterward
    clear_console()
    for deal in range(hand_size):  # player right of the first player deals (given random deck shuffling and lack of cheating by having the computer deal, doing the deal this (the usual) way is only for appearances)
        player_to_start_deal_to = (players_turn + num_players - 1) % num_players  # deal starts with the player left of the dealer
        for player_to_deal_to_offset in range(num_players):
            players[(player_to_start_deal_to + player_to_deal_to_offset) % num_players].cards_in_hand.append(draw_pile.pop())
    is_game_won = False

    while not is_game_won:
        player_to_play = players[players_turn]
        all_pawns = {}
        for player in players:
            all_pawns.update(player.pawns)
        if do_show_card_descriptions:
            print("    1: Move a friendly pawn forward one space, or move a friendly pawn from start.")
            print("    2: Move a friendly pawn forward two spaces, or move a friendly pawn from start. Draw again.")
            print("    3: Move a friendly pawn forward three spaces.")
            print("    4: Move a friendly pawn backward four spaces.")
            print("    5: Move a friendly pawn forward five spaces.")
            print(f"    7: Move a friendly pawn forward seven spaces, or split the movement between two {'or more ' if can_sevens_be_split_across_more_than_two_pawns else ''}friendly pawns.")
            print("    8: Move a friendly pawn forward eight spaces.")
            print("   10: Move a friendly pawn forward ten spaces, or move a friendly pawn backward one space.")
            print("   11: Move a friendly pawn forward eleven spaces, or swap the location of a friendly pawn and another player's pawn. (Does not work for pawns in their start, home, or safety zone.)")
            print("   12: Move a friendly pawn forward twelve spaces.")
            print("Sorry: Move a friendly pawn from start to a space occupied by another player's pawn, bumping that pawn back to its owner's start. (Does not work on pawns in their home or safety zone)")
        print_current_gameboard(all_pawns)
        if num_times_to_show_last_discard_pile != 0:
            num_times_to_show_last_discard_pile -= 1
            print_last_discard_pile(last_discard_pile)
        print_discard_pile(discard_pile)
        input(f"{get_text_color(player_to_play.name[0])}{player_to_play.name}'s{Color.RESET.value} turn (press enter to continue)") if player_to_play.player_type == PlayerType.HUMAN else print(f"{get_text_color(player_to_play.name[0])}{player_to_play.name}'s{Color.RESET.value} turn")
        if player_to_play.player_type == PlayerType.HUMAN:
            print_hand_of_cards(player_to_play)

        is_valid_play = False
        card_to_play = None
        if hand_size == 0:  # immediately draw the card if there are no hands of cards
            drawn_card, num_times_to_show_last_discard_pile = draw_card(draw_pile, discard_pile, last_discard_pile, num_times_to_show_last_discard_pile, num_players)
            player_to_play.cards_in_hand.append(drawn_card)
            card_to_play = player_to_play.cards_in_hand[0]
        is_card_a_ten_as_backward_one = False
        pawn_targets = []  # labels of pawn(s) to target (or contains 'd' if card is to be discarded); may also temporarily contain 'c' if play is not yet valid
        num_played_2s = 0  # count played '2's rather than have a boolean flag in case not is_immediate_draw_after_playing_a_2 so the correct number of extra draws can be known
        possible_plays = []
        while not is_valid_play:
            is_valid_play = True  # to be corrected as necessary
            if hand_size != 0:
                card_to_play = None  # reset
            if player_to_play.player_type == PlayerType.HUMAN:
                do_no_movement_for_2 = False
                while card_to_play not in player_to_play.cards_in_hand:
                    card_to_play = input("Card to play from your hand (choose by " + (f"index (1-{len(player_to_play.cards_in_hand)})" if player_to_play.card_select_method == CardSelectMethod.BY_INDEX else "value") + "): ").strip()  # this input can be stripped of surrounding spaces since the user can always correct their decision
                    if player_to_play.card_select_method == CardSelectMethod.BY_INDEX:
                        try:
                            card_to_play = int(card_to_play)  # correctly gives an error for empty input strings
                            if card_to_play not in range(1, len(player_to_play.cards_in_hand) + 1):
                                card_to_play = None
                            else:
                                card_to_play = player_to_play.cards_in_hand[card_to_play - 1]  # convert card_to_play to the value of the card to play to simplify (and expedite) both this while loop's condition and later code
                        except ValueError:
                            card_to_play = None
                            continue  # do nothing but ask for input again
                    if card_to_play in player_to_play.cards_in_hand:
                        selected_card_has_some_valid_play = False  # to be corrected as necessary
                        is_no_valid_movement_for_2 = True  # to be corrected as necessary
                        possible_plays = enumerate_possible_plays(player_to_play.cards_in_hand, player_to_play.name, all_pawns, are_teams, False, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played)
                        for possible_play in possible_plays:
                            if possible_play['card_to_play'] == card_to_play:
                                selected_card_has_some_valid_play = True
                                if card_to_play == '2':
                                    if possible_play['pawn_targets']:
                                        is_no_valid_movement_for_2 = False
                                    else:
                                        break
                                else:
                                    break
                        if not selected_card_has_some_valid_play:
                            print(f"Sorry, but you cannot play your {card_to_play} right now because no valid plays with it exist, though some valid play(s) exist for some other card(s) in your hand.")  # future consideration: list the card(s) in hand having valid play(s)
                            card_to_play = None
                        elif card_to_play == '2' and is_no_valid_movement_for_2:
                            if get_user_confirmation("No pawn can be moved with this 2. Play this 2 only to draw a card?"):
                                do_no_movement_for_2 = True
                            else:
                                card_to_play = None

                num_times_eleven_prompted_validly = 0  # an 11 is the only card that might have a valid move with both one and multiple (two) pawn targets, or might have an invalid first pawn target (since it would be assumed that one target is for a forward pawn movement but two targets are for a swap, unless the user is to be prompted an extra time) so its pawn targeting begets the extra loop condition
                seven_remaining_distance = 7  # only utilized when card_to_play == '7'
                pawn_targets = []  # reset
                if not do_no_movement_for_2:
                    pawn_target = None
                    while 'c' not in pawn_targets and (not is_valid_target(pawn_targets, card_to_play, player_to_play.name, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, is_card_a_ten_as_backward_one) or (num_times_eleven_prompted_validly == 1 and pawn_target)):  # have the user pick as many pawn targets as it takes to complete a valid move
                        pawn_target = None  # reset
                        if pawn_targets and card_to_play not in ['7', '10', '11', 'Sorry'] and not is_valid_target(pawn_targets, card_to_play, player_to_play.name, all_pawns, are_teams, can_sevens_be_split_across_more_than_two_pawns, is_card_a_ten_as_backward_one):  # if an invalid pawn_target was already provided for a card that requires exactly one pawn target and has no mistaking for what the move is intended to be (otherwise no possible moves with the last chosen pawn target has the last chosen pawn target removed separately), throw out the old/invalid pawn target
                            pawn_targets.pop()
                        is_some_possible_play = enumerate_possible_plays(player_to_play.cards_in_hand, player_to_play.name, all_pawns, are_teams, True, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played)
                        default_choice, default_choice_string = determine_default_action(card_to_play, pawn_targets, possible_plays, all_pawns, player_to_play.name, are_teams)
                        while pawn_target is None or (pawn_target not in all_pawns and pawn_target != 'c' and (pawn_target != 'd' or pawn_targets or is_some_possible_play) and (default_choice is None or pawn_target)):
                            pawn_target = input(f"Label of {'the (first)' if not pawn_targets else 'another'} pawn to target with card (such as {player_to_play.name[0]}1){',' if (num_played_2s == 0 or not is_card_after_playing_a_2_force_played) + (not pawn_targets and not is_some_possible_play) + (default_choice is not None) > 1 else (' or' if (num_played_2s == 0 or not is_card_after_playing_a_2_force_played) + (not pawn_targets and not is_some_possible_play) + (default_choice is not None) == 1 else '')}{' cancel/redo card choice (c)' if num_played_2s == 0 or not is_card_after_playing_a_2_force_played else ''}{',' if (num_played_2s == 0 or not is_card_after_playing_a_2_force_played) and ((not pawn_targets and not is_some_possible_play) or default_choice is not None) else ''}{' or' if (pawn_targets or is_some_possible_play) and default_choice is not None else ''}{' discard card (d)' if (not pawn_targets and not is_some_possible_play) else ''}{',' if (not pawn_targets and not is_some_possible_play) and default_choice is not None else ''}{' or' if default_choice is not None else ''}{f' go with the default choice of {default_choice_string} (input nothing)' if default_choice is not None else ''}: ")
                        if not pawn_target:
                            if not isinstance(pawn_targets, dict):
                                pawn_targets += default_choice  # default_choice has already been confirmed to not be None if len(pawn_target) == 0
                        else:
                            if not isinstance(pawn_targets, dict):
                                pawn_targets.append(pawn_target)
                            else:
                                pawn_targets[pawn_target] = 0  # arbitrarily initialize to zero
                        if (not isinstance(pawn_targets, dict) and pawn_targets[len(pawn_targets) - 1] not in ['c', 'd']) or (isinstance(pawn_targets, dict) and list(pawn_targets.keys())[len(pawn_targets) - 1] not in ['c', 'd']):
                            if card_to_play == '7':
                                if pawn_target:  # for '7's, only request distance input if default choice was not utilized
                                    distance_to_move_pawn = 0
                                    while (isinstance(distance_to_move_pawn, str) and distance_to_move_pawn != 'c') or distance_to_move_pawn <= 0 or distance_to_move_pawn > seven_remaining_distance:
                                        distance_to_move_pawn = input(f"How many spaces to move {list(pawn_targets.keys())[len(pawn_targets) - 1] if isinstance(pawn_targets, dict) else pawn_targets[len(pawn_targets) - 1]} (1-{seven_remaining_distance}) or cancel/redo card choice (c): ")
                                        if distance_to_move_pawn != 'c':
                                            try:
                                                distance_to_move_pawn = int(distance_to_move_pawn)
                                            except ValueError:
                                                continue  # do nothing but ask for input again
                                    if distance_to_move_pawn == 'c':
                                        pawn_targets.pop(list(pawn_targets.keys())[len(pawn_targets) - 1])
                                        pawn_targets[len(pawn_targets) - 1] = 'c'
                                    else:
                                        if not isinstance(pawn_targets, dict):
                                            pawn_targets = {pawn_target: distance_to_move_pawn}  # update pawn_targets to be a dictionary specifying how much this/each pawn is desired to be moved
                                        else:
                                            pawn_targets[pawn_target] = distance_to_move_pawn
                                        if not is_some_valid_split_for_seven(pawn_targets, player_to_play.name, all_pawns, are_teams, seven_remaining_distance, can_sevens_be_split_across_more_than_two_pawns):  # verify there is some valid movement given the current movement distribution of the seven, otherwise call the last provided pawn target invalid
                                            pawn_targets.pop(pawn_target)  # remove invalid pawn selection
                                else:
                                    if not isinstance(pawn_targets, dict):
                                        pawn_targets = default_choice  # update pawn_targets to be a dictionary specifying how much this/each pawn is desired to be moved
                                    else:
                                        pawn_targets.update(default_choice)
                            elif card_to_play == '10':
                                if is_some_valid_move_for_ten(pawn_targets, player_to_play.name, all_pawns, are_teams):  # if at least one of the ways to play the ten are valid, ask the user for which method they intended (then again check if what they chose is valid)
                                    is_card_a_ten_as_backward_one = ('b' if "backward" in default_choice_string else ('f' if "forward" in default_choice_string else None))
                                    while is_card_a_ten_as_backward_one not in ['c', 'b', 'f']:
                                        is_card_a_ten_as_backward_one = input(f"Do you want to use this card to move {pawn_targets[len(pawn_targets) - 1]} forward (f) by ten spaces, backward (b) by one space, or cancel/redo card choice (c)? ")
                                    if is_card_a_ten_as_backward_one == 'c':
                                        pawn_targets[len(pawn_targets) - 1] = 'c'
                                        is_card_a_ten_as_backward_one = False  # reset
                                    else:
                                        is_card_a_ten_as_backward_one = (is_card_a_ten_as_backward_one == 'b')
                                else:
                                    pawn_targets.pop()  # remove invalid pawn selection
                            elif card_to_play == '11':
                                is_some_valid_swap = is_some_valid_swap_for_eleven(pawn_targets[0], player_to_play.name, all_pawns, are_teams)
                                num_times_eleven_prompted_validly += is_some_valid_swap  # ignore counting this prompt for the eleven card if the response was unacceptable
                                if not is_some_valid_swap:
                                    pawn_targets.pop()  # remove invalid pawn selection
                            elif card_to_play == 'Sorry':
                                if not is_some_valid_play_for_sorry(pawn_targets[0], player_to_play.name, all_pawns, are_teams):
                                    pawn_targets.pop()  # remove invalid pawn selection
                    if 'd' in pawn_targets:
                        continue
                if 'c' in pawn_targets:
                    is_valid_play = False
                elif card_to_play == '2':  # play the 2 then continue the player's turn by having them choose an additional card to play
                    num_played_2s += 1
                    if not do_no_movement_for_2:
                        play_card(card_to_play, pawn_targets, all_pawns)
                        pawn_targets = []  # reset
                        for pawn in all_pawns:  # need to update the players' copies of the pawns with any adjustments
                            for player in players:
                                if player.name[0] == pawn[0]:
                                    player.pawns.update({pawn: all_pawns[pawn]})
                                    break
                    player_to_play.cards_in_hand.remove(card_to_play)
                    discard_pile.append(card_to_play)
                    if is_immediate_draw_after_playing_a_2:
                        drawn_card, num_times_to_show_last_discard_pile = draw_card(draw_pile, discard_pile, last_discard_pile, num_times_to_show_last_discard_pile, num_players)
                        player_to_play.cards_in_hand.append(drawn_card)
                        if is_card_after_playing_a_2_force_played:  # otherwise card_to_play will be reset at the beginning of the next loop iteration
                            card_to_play = drawn_card
                    is_valid_play = False  # need to complete the play by playing another card
                    print_current_gameboard(all_pawns)
                    if num_times_to_show_last_discard_pile != 0:
                        print_last_discard_pile(last_discard_pile)
                    print_discard_pile(discard_pile)
                    print("(You just played a 2.)")
                    print_hand_of_cards(player_to_play)
            else:  # player_to_play.player_type == PlayerType.COMPUTER
                is_turn_done = False
                forced_card = []
                while not is_turn_done:
                    is_turn_done = True  # to be corrected as necessary
                    possible_plays = enumerate_possible_plays(player_to_play.cards_in_hand if not forced_card else forced_card, player_to_play.name, all_pawns, are_teams, False, can_sevens_be_split_across_more_than_two_pawns, is_immediate_draw_after_playing_a_2, is_card_after_playing_a_2_force_played, discard_pile)
                    max_score = 0
                    index_of_play_with_max_score = None
                    index = 0
                    for possible_play in possible_plays:
                        if possible_play['play_score'] > max_score:
                            max_score = possible_play['play_score']
                            index_of_play_with_max_score = index
                        index += 1
                    card_to_play = possible_plays[index_of_play_with_max_score]['card_to_play']
                    pawn_targets = possible_plays[index_of_play_with_max_score]['pawn_targets']
                    if card_to_play == '2':
                        num_played_2s += 1
                        is_turn_done = False
                        if pawn_targets:
                            play_card(card_to_play, pawn_targets, all_pawns, is_card_a_ten_as_backward_one)
                            for pawn in all_pawns:  # need to update the players' copies of the pawns with any adjustments
                                for player in players:
                                    if player.name[0] == pawn[0]:
                                        player.pawns.update({pawn: all_pawns[pawn]})
                                        break
                        player_to_play.cards_in_hand.remove(card_to_play)
                        discard_pile.append(card_to_play)
                        if is_immediate_draw_after_playing_a_2:  # if best play requires waiting to see the next drawn card
                            drawn_card, num_times_to_show_last_discard_pile = draw_card(draw_pile, discard_pile, last_discard_pile, num_times_to_show_last_discard_pile, num_players)
                            player_to_play.cards_in_hand.append(drawn_card)
                            if is_card_after_playing_a_2_force_played:  # otherwise card_to_play will be reset at the beginning of the next loop iteration
                                card_to_play = drawn_card
                                forced_card = [card_to_play]
                    else:  # the last card to play gets handled by the logic following the loop
                        is_card_a_ten_as_backward_one = possible_plays[index_of_play_with_max_score]['is_card_a_ten_as_backward_one'] if 'is_card_a_ten_as_backward_one' in possible_plays[index_of_play_with_max_score] else False

        if 'd' not in pawn_targets:
            play_card(card_to_play, pawn_targets, all_pawns, is_card_a_ten_as_backward_one)
            for pawn in all_pawns:  # need to update the players' copies of the pawns with any adjustments
                for player in players:
                    if player.name[0] == pawn[0]:
                        player.pawns.update({pawn: all_pawns[pawn]})
                        break
        player_to_play.cards_in_hand.remove(card_to_play)
        discard_pile.append(card_to_play)
        if hand_size != 0:
            drawn_card, num_times_to_show_last_discard_pile = draw_card(draw_pile, discard_pile, last_discard_pile, num_times_to_show_last_discard_pile, num_players)
            player_to_play.cards_in_hand.append(drawn_card)
            if num_played_2s != 0 and not is_immediate_draw_after_playing_a_2:  # if it's time to draw the extra card(s) for having played some number of '2's
                for i in range(num_played_2s):
                    drawn_card, num_times_to_show_last_discard_pile = draw_card(draw_pile, discard_pile, last_discard_pile, num_times_to_show_last_discard_pile, num_players)
                    player_to_play.cards_in_hand.append(drawn_card)
            if player_to_play.player_type == PlayerType.HUMAN:
                print_hand_of_cards(player_to_play)  # allow the user to see their draw before yielding their turn to the next player
                input("Press enter to complete your turn.")
        if player_to_play.player_type == PlayerType.HUMAN:
            clear_console()

        is_game_won = True  # to be corrected as necessary
        for pawn in player_to_play.pawns:
            if player_to_play.pawns[pawn] != SpecialLocation.HOME.value:
                is_game_won = False
                break
        if are_teams and is_game_won:
            for pawn in players[(players_turn + 2) % num_players].pawns:
                if players[(players_turn + 2) % num_players].pawns[pawn] != SpecialLocation.HOME.value:
                    is_game_won = False
                    break
        players_turn += 1
        players_turn %= num_players

    print("State of the game board:")
    all_pawns = {}
    for player in players:
        all_pawns.update(player.pawns)
    print_board(all_pawns)
    victors = []
    for player in players:
        is_player_victor = True  # to be corrected as necessary
        for pawn in player.pawns:
            if player.pawns[pawn] != SpecialLocation.HOME.value:
                is_player_victor = False
                break
        if is_player_victor:
            victors.append(player.name)
    print(victors[0] + (" and " + victors[1] if len(victors) == 2 else ""), "won! Congratulations!")
    return 0


sorry_boardgame()  # execute
