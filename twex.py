"""A module for reading two-level examples

The examples are assumed to be as space-separated one-level
representation and they are compiled into a single automaton. 
At the same time, the alphabet used in the examples is 
collected in several forms.

    EXAMPLES_FST -- the transducer which accepts exactly the examples

    symbol_pair_set -- a tuple of string pairs suitable for
        e.g. hfst.rules.restriction

"""
import hfst, re, twbt

def label2pair(label):
    m = re.match(r"^([^:]*):([^:]*)$", label)
    if m:
        return(m.group(1), m.group(2))
    else:
        return(label, label)

symbol_pair_set = set()
input_symbol_set = set()
output_symbol_set = set()
pair_symbols_for_input = {}
pair_symbols_for_output = {}

example_set = set()
example_list = []
EXAMPLES_FST = hfst.HfstTransducer()
EXAMPLE_FST_LIST = []

def read_examples(filename="test.pairstr"):
    """Reads the examples from the file whose name is 'filename'.

Use help(twex) in order to get more information.
"""
    global symbol_pair_set, EXAMPLES_FST, pair_symbols_for_input, example_list
    EXAMPLES_FST.set_name(filename)
    exfile = open(filename,"r")
    for line in exfile:
        lin = "§ " + line.strip() + " §"
        lst = re.split(" +", lin)
        example_set.add(" ".join(lst)) # spaces normalized
        example_list.append(" ".join(lst))
        line_tok = [label2pair(label) for label in lst ]
        # print(line_tok) ##
        line_fst = hfst.tokenized_fst(line_tok)
        # twbt.printfst(line_fst, True) ##
        EXAMPLES_FST.disjunct(line_fst)
        for insym, outsym in line_tok:
            # print(insym, outsym, end="") ##
            symbol_pair_set.add((insym, outsym))
    exfile.close()
    # symbol_pair_set.add(('Ø', 'Ø')) ### ?
    #print("List of alphabet symbols:", sorted(symbol_pair_set)) ##
    EXAMPLES_FST.minimize()
    # twbt.printfst(EXAMPLES_FST, False) ##
    for insym, outsym in symbol_pair_set:
        input_symbol_set.add(insym)
        output_symbol_set.add(outsym)
    for insym in input_symbol_set:
        pair_symbols_for_input[insym] = set()
    for outsym in output_symbol_set:
        pair_symbols_for_output[outsym] = set()
    for insym, outsym in symbol_pair_set:
        pair_symbol = insym if insym == outsym else insym + ":" + outsym
        pair_symbols_for_input[insym].add(pair_symbol)
        pair_symbols_for_output[outsym].add(pair_symbol)

def positive_examples(input_symbols):
    global pair_symbols_for_input
    result = set()
    insyms = set()
    for insym in input_symbols:
        # print("insym:", insym) ##
        insyms = insyms | pair_symbols_for_input[insym]
    pairsymlist = [re.sub(r'([}{])', r'\\\1', psym)
                   for psym
                   in insyms]
    pattern = re.compile("|".join(pairsymlist))
    for example in example_set:
        if pattern.search(example):
            result.add(example)
    return(result)

negative_example_set = set()

def blur_output_symbol(input_symbols, result_list, remaining_list):
    global negative_example_set
    # print("result/remaining list;", result_list, remaining_list) ##
    if not remaining_list:
        negative_example_set.add(" ".join(result_list))
        return
    else:
        resl = result_list.copy()
        reml = remaining_list.copy()
        pairsym = reml[0]
        insym, outsym = label2pair(pairsym)
        if insym not in input_symbols:
            resl.append(pairsym)
            # print("res, remain:", resl, reml) ##
            blur_output_symbol(input_symbols, resl, reml[1:])
        else:
            for pairsym in pair_symbols_for_input[insym]:
                resl = result_list.copy()
                resl.append(pairsym)
                # print("res, remain:", resl, reml) ##
                blur_output_symbol(input_symbols, resl, reml[1:])
                
def negative_examples(input_symbols):
    global negative_example_set
    pos_exs = positive_examples(input_symbols)
    negative_example_set = set()
    for example in pos_exs:
        ex_as_list = re.split(" ", example)
        blur_output_symbol(input_symbols, [], ex_as_list)
    for example in pos_exs:
        negative_example_set.discard(example)
    return(negative_example_set)
    

if __name__ == "__main__":
    read_examples()
    print("symbol_pair_set =", symbol_pair_set)
    # for ex in example_set: ##
    #     print(ex) ##
    print("pair_symbols_for_input:", pair_symbols_for_input) ##
    print("positive examples:")
    for ex in positive_examples({"{ao}", "{ij}"}):
        print(ex)
    print("negative examples:")
    for ex in negative_examples({"{ao}", "{ij}"}):
        print(ex)
