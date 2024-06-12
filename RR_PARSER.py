def grammar_string_to_dict(grammar_string):
    productions = [production.strip() for production in grammar_string.split('\n')]
    grammar_dict = {}
    for production in productions:
        left, right = production.split('->')
        left = left.strip()
        right = right.strip()
        rhs_alternatives = right.split('|')
        alternative_lists = []
        for alternative in rhs_alternatives:
            components = alternative.split()
            alternative_lists.append(components)
        grammar_dict[left] = alternative_lists
    return grammar_dict

def eliminate_right_recursion(grammar_dict):
    # Iterate over the non-terminals in the grammar_dict
    for non_terminal, alternatives in list(grammar_dict.items()):
        alpha = []
        beta = []
        for alternative in alternatives:
            if alternative and alternative[-1] == non_terminal:
                alpha.append(alternative[:-1])
            else:
                if alpha:
                    beta.append(alternative)
        if alpha:
            new_terminal = non_terminal + '*'
            # Create the alpha entries with the non-terminal + '*' and elements of alpha
            alpha_entries = [[new_terminal] + entry for entry in alpha]
            # Add the epsilon (ε) entry to alpha
            alpha_entries.append(["epi"])
            grammar_dict[new_terminal] = alpha_entries
            # Replace the original alternatives with beta lists
            grammar_dict[non_terminal] = [[new_terminal] + entry for entry in beta]

# Function to find lists with common suffix elements and their uncommon parts
def find_lists_with_common_suffix_and_uncommon_parts(data_dict):
    common_suffix_data = {}
    for key, data in data_dict.items():
        common_suffix_data[key] = {}
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                list1 = data[i]
                list2 = data[j]
                # Find the common suffix of list1 and list2
                suffix = []
                min_len = min(len(list1), len(list2))
                for k in range(1, min_len + 1):
                    if list1[-k] == list2[-k]:
                        suffix.insert(0, list1[-k])
                    else:
                        break
                # If there is a common suffix, add it to the result
                if suffix:
                    if tuple(suffix) not in common_suffix_data[key]:
                        common_suffix_data[key][tuple(suffix)] = {'common_lists': [], 'uncommon_parts': []}
                    common_suffix_data[key][tuple(suffix)]['common_lists'].append([list1, list2])
                    # Find and store the uncommon parts
                    uncommon_part1 = [list1[:-len(suffix)]]
                    uncommon_part2 = [list2[:-len(suffix)]]    
                    if uncommon_part1 not in common_suffix_data[key][tuple(suffix)]['uncommon_parts']:
                        common_suffix_data[key][tuple(suffix)]['uncommon_parts'].append(uncommon_part1)
                    if uncommon_part2 not in common_suffix_data[key][tuple(suffix)]['uncommon_parts']:
                        common_suffix_data[key][tuple(suffix)]['uncommon_parts'].append(uncommon_part2)
    # Remove keys with empty values
    common_suffix_data = {k: v for k, v in common_suffix_data.items() if v} 
    return common_suffix_data

def right_factorization(grammar_dict, common_suffix_data):
    for non_terminal, suffix_data in common_suffix_data.items():
        if non_terminal in grammar_dict:
            for suffix, data in suffix_data.items():
                # print(f"suffix: {suffix} data: {data}")
                new_terminal = non_terminal + '#'
                while new_terminal in grammar_dict:
                    new_terminal = new_terminal + '#'
                new_list = [new_terminal]
                for values in suffix:
                    new_list.append(values)
                # Append the combined_suffix list to grammar_dict[non_terminal]
                grammar_dict[non_terminal].append(new_list)
                common_lists = data['common_lists']
                for common_list in common_lists:
                    for sublist in common_list:
                        if sublist in grammar_dict[non_terminal]:
                            grammar_dict[non_terminal].remove(sublist)
                # to save the uncommon parts for the new_terminal values
                if 'uncommon_parts' in data:
                    uncommon_parts = data['uncommon_parts']
                else:
                    uncommon_parts = []
                grammar_dict[new_terminal] = [part for sublist in uncommon_parts for part in sublist]


def find_last(grammar_dict, key):
    last = set()
    alternatives = grammar_dict[key]
    for alternative in alternatives:
        position = -1
        current_last = set()
        changed = False
        while not changed:
            last_symbol = alternative[position]
            if last_symbol in grammar_dict:
                borrow_list = find_last(grammar_dict, last_symbol)
                if "epi" in borrow_list:
                    borrow_list.discard("epi")
                    current_last.update(borrow_list)
                    position -= 1
                    if abs(position) > len(alternative):
                        current_last.add("epi")
                    changed = True  # Set 'changed' to True here
                else:
                    current_last.update(borrow_list)
                    changed = True
            else:
                current_last.add(last_symbol)
                changed = True
        last.update(current_last)
    return last

def find_all_last(grammar_dict):
    all_lasts = {}
    for non_terminal in grammar_dict:
        last_set = find_last(grammar_dict, non_terminal)
        all_lasts[non_terminal] = last_set
    return all_lasts


def calculate_precedences(grammar_dict, last_sets, key):
    precedences = set()  # Initialize a set to store the calculated precedences for the specific non-terminal.
    for non_terminal, productions in grammar_dict.items():
        # Iterate through the productions of the current non-terminal.
        for production in productions:
            updated = False  # Initialize the 'updated' flag for each production.
            non_terminal_position = None
            preceding_symbol = None
            # Find the position and preceding symbol of the specified non-terminal in the production.
            for i, symbol in enumerate(production):
                if symbol == key:
                    non_terminal_position = i
                    if non_terminal_position > 0:
                        preceding_symbol = production[non_terminal_position - 1]
                        break
            while not updated and non_terminal_position is not None :
                changed_precedence = False
                if non_terminal_position == 0 and not changed_precedence:# If non_terminal_position is 0, assign the precedence of the non-terminal.
                    if key == non_terminal:  # Skip the same key if present on LHS
                        updated = True
                        continue
                    borrow = calculate_precedences(grammar_dict, last_sets, non_terminal)
                    precedences.update(borrow)
                    updated = True
                elif preceding_symbol is not None:
                    if preceding_symbol in grammar_dict:
                        if "epi" not in last_sets[preceding_symbol]:
                            precedences.update(last_sets[preceding_symbol])
                            updated = True
                        else:
                            add = [s for s in last_sets[preceding_symbol] if s != "epi"]
                            precedences.update(add)
                        if non_terminal_position - 1 < 0:
                            borrow = calculate_precedences(grammar_dict, last_sets, non_terminal)
                            precedences.update(borrow)
                            updated = True
                        else:
                            non_terminal_position = non_terminal_position -1
                            preceding_symbol = production[non_terminal_position - 1]  # Backtrack
                            changed_precedence = True
                    else:
                        precedences.update(preceding_symbol)
                        updated = True
    # If the specified non-terminal is the first key in grammar_dict, add the precedence of '$'.
    if key == list(grammar_dict.keys())[0]:
        precedences.add('$')
    return precedences  # Return the set containing the precedences for the specified non-terminal.

def calculate_all_precedences(grammar_dict, last_sets):
    all_precedences = {}  # Initialize a dictionary to store all calculated precedences.
    for non_terminal in grammar_dict:
        precedences = calculate_precedences(grammar_dict, last_sets, non_terminal)
        all_precedences[non_terminal] = precedences
    return all_precedences  # Return the dictionary containing all the precedences.


def create_parsing_table(grammar_dict, last_sets, all_precedences):
    parsing_table = {}  # Initialize the parsing table
    for non_terminal, alternatives in grammar_dict.items():
        for alternative in alternatives:
            position = -1# saying that it is last of list
            changed = False
            while not changed:
                # Get the last symbol of the alternative
                last_symbol = alternative[position]
                # Check if the last symbol is in the grammar dictionary
                if last_symbol in grammar_dict:
                    if 'epi' in last_sets[last_symbol]:
                        add = [s for s in last_sets[last_symbol] if s != "epi"]
                        for val in add:
                            parsing_table[(non_terminal, val)] = alternative
                        position -= 1
                        if abs(position) > len(alternative): #all elements are already checked
                            parsing_table[(non_terminal, 'epi')] = alternative
                            changed = True 
                    else:
                        for val in last_sets[last_symbol]:
                            parsing_table[(non_terminal, val)] = alternative
                            changed = True
                elif last_symbol != 'epi':# If not in the grammar dictionary and not epsilon, add it to the table
                    parsing_table[(non_terminal, last_symbol)] = alternative
                    changed = True
                else:
                    for val in all_precedences[non_terminal]:
                        parsing_table[(non_terminal, val)] = ['epi']
                    changed = True
    return parsing_table

def print_parsing_table(parsing_table, grammar_dict, terminals):
    # Print the header row with terminal symbols and '$'
    header = [""] + terminals
    header = [f"{symbol:10}" for symbol in header]
    print(" | ".join(header))
    # Print the parsing table entries
    for non_terminal in grammar_dict.keys():
        row = [non_terminal.ljust(10)]  # Left-justify and pad to 10 characters
        for terminal in terminals:
            entry = parsing_table.get((non_terminal, terminal), [])
            entry_text = " ".join(entry)
            entry_text = entry_text[:10]  # Truncate or pad to a maximum of 10 characters
            row.append(f"{entry_text:10}")
        print(" | ".join(row))

def string_acceptance(parsing_table, input_string):
    input_stack = ['$'] + list(input_string.split())
    parse_stack = ['$'] + [list(parsing_table.keys())[0][0]]  # Initialize parse stack with the starting non-terminal

    while input_stack and parse_stack:
        parse_stack_top = parse_stack[-1]
        input_stack_top = input_stack[-1]
        # print( f" parse stack - {parse_stack} top {parse_stack_top}")
        # print(f"input stack - {input_stack} top {input_stack_top}")
        if parse_stack_top == input_stack_top:
            parse_stack.pop()
            input_stack.pop()

        else:
            try:
                table_entry = parsing_table[(parse_stack_top, input_stack_top)]
                parse_stack.pop()
                if table_entry != ['epi']:
                    parse_stack.extend(table_entry)
            except KeyError:
                # print("The string is not in the grammar")
                break

    if not input_stack and not parse_stack:# Both input_stack and parse_stack are empty
        print("--The string is accepted by the grammar")
    else:
        print("--The string is not accepted by the grammar")


# Example usage with the provided grammar_string
grammar_string = """L->C ; L| C ;
C->ser B| par B| id | num
B->C B |end"""

grammar_dict = grammar_string_to_dict(grammar_string)

eliminate_right_recursion(grammar_dict)
print("AFTER ELIMINATING RIGHT RECURSTION")
for non_terminal, alternatives in grammar_dict.items():
    print(f"{non_terminal}: {alternatives}")


common_suffix_data = find_lists_with_common_suffix_and_uncommon_parts(grammar_dict)
right_factorization(grammar_dict, common_suffix_data)
print("AFTER RIGHT FACTORISATION")
for non_terminal, alternatives in grammar_dict.items():
    print(f"{non_terminal}: {alternatives}")


last_sets = find_all_last(grammar_dict)
for non_terminal, last_set in last_sets.items():
    print(f'Last({non_terminal}) = {last_set}')

all_precedences = calculate_all_precedences(grammar_dict, last_sets)
for non_terminal, precedences in all_precedences.items():
    print(f"Precedences({non_terminal}) = {precedences}")


# Usage:
terminals = []
for alternatives in grammar_dict.values():
    for alternative in alternatives:
        for symbol in alternative:
            if symbol not in grammar_dict and symbol not in terminals:
                terminals.append(symbol)
terminals.append('$')  # Add the end marker '$'

parsing_table = create_parsing_table(grammar_dict, last_sets, all_precedences )
print_parsing_table(parsing_table, grammar_dict, terminals)

def preprocess_input(input_string, terminals):
    tokens = input_string.split()
    for i in range(len(tokens)):
        if tokens[i] not in terminals:
            if tokens[i].isdigit():
                tokens[i] = 'num'
            else:
                tokens[i] = 'id'
    preprocessed_input = ' '.join(tokens)
    return preprocessed_input

# Read input from the file, treating each line as a test case
file_name = "input.txt"
with open(file_name, 'r') as file:
    test_cases = file.readlines()  # Read all lines from the file

for index, test_case in enumerate(test_cases):
    input_string = test_case.strip()
    # Display the test case (optional)
    print(f"Test Case {index + 1}: {input_string}")
    # input_string = input("Enter a string to check for acceptance: ")
    preprocessed_input = preprocess_input(input_string, terminals)
    string_acceptance(parsing_table, preprocessed_input)
