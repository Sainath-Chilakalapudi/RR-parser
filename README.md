# LL(1)-Style Parser with Right Recursion Elimination and Right Factoring

This repository contains a Python implementation of a grammar analysis and parsing system. It processes a context-free grammar, eliminates **right recursion**, applies **right factoring**, and builds a **reverse LL(1)-style parsing table** using the **last sets** and **precedence rules**. The parser then uses the table to **check string acceptance**.

---

## ✨ Features

* Accepts grammar input in BNF-like format
* Eliminates **right recursion**
* Performs **right factoring** based on common suffixes
* Computes **Last sets** and **precedence** for non-terminals
* Builds a **reverse LL(1)-like parsing table**
* Supports token preprocessing (`num`, `id`)
* Verifies whether input strings are **accepted** by the grammar
* Handles multiple test cases via an `input.txt` file

---

## 📝 Grammar Format

* Each production must be on a **separate line**
* Use `->` for production rules
* Separate productions of a non-terminal with `|`
* Use `epi` to denote **epsilon** (empty string)
* Only **uppercase** symbols are **non-terminals**, everything else is **terminal**
* The **first production** defines the **start symbol**

### Example:

```txt
L -> C ; L | C ;
C -> ser B | par B | id | num
B -> C B | end
```

---

## 📥 Input File Format

* Input strings should be space-separated tokens
* Valid terminals include: `ser`, `par`, `end`, etc.
* Numbers are treated as `num` and unknown identifiers as `id`
* All strings must **end with `$`**

### Example `input.txt`:

```txt
ser num end $
par id ser id end end $
id $
```

---

## 🧠 How It Works

1. **Parsing and Preprocessing**

   * Reads and stores the grammar
   * Eliminates right recursion and factors the grammar

2. **Grammar Analysis**

   * Computes the `Last` set for each non-terminal
   * Derives `precedence` sets using last sets

3. **Table Construction**

   * Generates a reverse parsing table for bottom-up acceptance

4. **String Acceptance**

   * Simulates parsing with a stack
   * Uses the parsing table to validate each input string

---

## ✅ Sample Output

```txt
AFTER ELIMINATING RIGHT RECURSION
...
AFTER RIGHT FACTORISATION
...
Last(L) = {';', 'id', 'num', ...}
Precedences(L) = {'$', ...}

Parsing Table:
            |     ser     |     par     |      ;      |     id      |     num     |     end     |      $      
----------------------------------------------------------------------------------------------
L           |   L# C      |   L# C      |             |   L# C      |   L# C      |             |             
...

Test Case 1: ser num end $
--The string is accepted by the grammar

Test Case 2: par id ser id end end $
--The string is accepted by the grammar

Test Case 3: id $
--The string is accepted by the grammar
```

---

## 🚀 How to Run

1. Add your grammar inside the `grammar_string` variable in `parser.py`
2. Save input strings in `input.txt`, one per line
3. Run the parser:

```bash
python parser.py
```
