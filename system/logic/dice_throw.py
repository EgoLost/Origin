import random
import re


def Dnd_dices_throw(value):
    values = value.lower()
    throw = values.split("d")

    if len(throw) != 2 or not all(part.isdigit() for part in throw):
        return False

    amount = int(throw[0])
    sides = int(throw[1])

    if amount <= 0 or sides <= 0:
        return False

    result = []

    for _ in range(amount):
        result.append(random.randint(1, sides))

    return result


def Fate_dices_throw(value):
    values = value.lower()

    if not values.endswith("df") or not values[:-2].isdigit():
        return False

    amount = int(values[:-2])

    if amount <= 0:
        return False

    result = []

    for _ in range(amount):
        result.append(random.choice([-1, 0, 1]))

    return result


def dice_expression(value):
    expression = value.lower().replace(" ", "")

    pattern = r"[+-]?(?:\d+d(?:\d+|f)|\d+)"
    tokens = re.findall(pattern, expression)

    if "".join(tokens) != expression or not tokens:
        return False

    total = 0
    rolls = []

    for token in tokens:
        sign = -1 if token.startswith("-") else 1
        dice = token.lstrip("+-")

        if "d" in dice:
            if dice.endswith("f"):
                result = Fate_dices_throw(dice)
            else:
                result = Dnd_dices_throw(dice)

            if result is False:
                return False

            subtotal = sum(result)
            rolls.append((token, result, sign * subtotal))
            total += sign * subtotal

        else:
            total += int(token)

    return {
        "total": total,
        "rolls": rolls
    }


print(dice_expression("4d10 + 4d4 - 3"))
print(dice_expression("4d10"))
print(dice_expression("4dF + 3dF"))

print(Fate_dices_throw("5dF"))
print(Fate_dices_throw("5d5F"))
print(Fate_dices_throw("4dF"))
print(Dnd_dices_throw("3d8"))
print(Dnd_dices_throw("3d84"))
print(Dnd_dices_throw("3d8d3"))