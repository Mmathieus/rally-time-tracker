from prompt_toolkit import prompt as prmnt
from prompt_toolkit.completion import WordCompleter


def get_user_input(symbol='◇', prompt="Select an option", with_colon=True, lowercase=True, autocomplete_options=None, align_width=None) -> str:
    colon = ':' if with_colon else ''
    label = f"{symbol} {prompt}{colon}"
    
    if align_width:
        label = label.ljust(align_width)
    
    final_prompt = f"{label} "
    
    if autocomplete_options:
        completer = WordCompleter(autocomplete_options, ignore_case=True)
        user_input = prmnt(message=final_prompt, completer=completer, complete_while_typing=True).strip()
    else:
        user_input = input(final_prompt).strip()
        
    return user_input.lower() if lowercase else user_input
